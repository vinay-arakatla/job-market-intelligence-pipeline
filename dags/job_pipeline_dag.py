"""Apache Airflow DAG for job market intelligence pipeline"""

from datetime import datetime, timedelta
from typing import Any, Dict

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.decorators import dag

from src.extract.jobspy_extractor import JobSpyExtractor
from src.load.db_loader import DatabaseLoader
from src.quality.data_validator import validate_dataframe
from src.scoring.score_calculator import score_jobs_from_dataframe
from src.scoring.skill_extractor import extract_skills_for_jobs
from src.transform.data_cleaner import DataCleaner
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# DAG Configuration
default_args = {
    "owner": "data-engineer",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "start_date": datetime(2026, 6, 1),
}

# Create DAG
dag = DAG(
    "job_market_intelligence_pipeline",
    default_args=default_args,
    description="ETL pipeline for job market analysis and scoring",
    schedule_interval="0 9 * * *",  # Daily at 9 AM
    catchup=False,
    tags=["job-market", "etl", "data-pipeline"],
)


# Task 1: Extract jobs from JobSpy
def extract_jobs_task(**context: Dict[str, Any]) -> None:
    """Extract jobs using JobSpy"""
    logger.info("Starting job extraction task")

    extractor = JobSpyExtractor()
    jobs_df = extractor.extract_jobs()

    if not jobs_df.empty:
        jobs_df = extractor.validate_extracted_data(jobs_df)
        logger.info(f"Extracted {len(jobs_df)} jobs")

        # Store in XCom for next task
        context["task_instance"].xcom_push(key="extracted_jobs", value=jobs_df)
    else:
        logger.warning("No jobs extracted")
        context["task_instance"].xcom_push(key="extracted_jobs", value=None)


# Task 2: Load raw jobs to database
def load_raw_jobs_task(**context: Dict[str, Any]) -> None:
    """Load extracted jobs into raw_job_postings table"""
    logger.info("Starting raw job load task")

    jobs_df = context["task_instance"].xcom_pull(
        task_ids="extract_jobs", key="extracted_jobs"
    )

    if jobs_df is None or jobs_df.empty:
        logger.warning("No jobs to load")
        return

    loader = DatabaseLoader()
    try:
        inserted, skipped = loader.load_raw_jobs(jobs_df)
        logger.info(f"Loaded {inserted} jobs, skipped {skipped} duplicates")
        context["task_instance"].xcom_push(
            key="load_stats", value={"inserted": inserted, "skipped": skipped}
        )
    finally:
        loader.disconnect()


# Task 3: Clean raw jobs
def clean_jobs_task(**context: Dict[str, Any]) -> None:
    """Clean and transform raw job data"""
    logger.info("Starting job cleaning task")

    loader = DatabaseLoader()
    try:
        # Query raw jobs from database
        query = """
            SELECT * FROM raw_job_postings
            WHERE scraped_date >= NOW() - INTERVAL '1 day'
            AND raw_job_id NOT IN (
                SELECT raw_job_id FROM cleaned_job_postings
            )
            LIMIT 1000
        """
        results = loader.execute_query(query)

        if not results:
            logger.warning("No raw jobs to clean")
            return

        # Convert to DataFrame
        import pandas as pd

        raw_jobs = pd.DataFrame(
            results,
            columns=[
                "raw_job_id",
                "source_platform",
                "search_keyword",
                "title",
                "company",
                "location",
                "job_type",
                "job_level",
                "salary_min",
                "salary_max",
                "salary_currency",
                "salary_interval",
                "posted_date",
                "scraped_date",
                "job_url",
                "company_url",
                "description",
                "raw_data_json",
                "created_at",
                "updated_at",
            ],
        )

        # Clean
        cleaner = DataCleaner()
        cleaned_df = cleaner.clean_dataframe(raw_jobs)
        unique_df, duplicates = cleaner.detect_duplicates(cleaned_df)

        logger.info(f"Cleaned {len(unique_df)} unique jobs")
        context["task_instance"].xcom_push(key="cleaned_jobs", value=unique_df)

    finally:
        loader.disconnect()


# Task 4: Extract skills
def extract_skills_task(**context: Dict[str, Any]) -> None:
    """Extract skills from job descriptions"""
    logger.info("Starting skill extraction task")

    cleaned_df = context["task_instance"].xcom_pull(
        task_ids="clean_jobs", key="cleaned_jobs"
    )

    if cleaned_df is None or cleaned_df.empty:
        logger.warning("No cleaned jobs for skill extraction")
        return

    skills_df = extract_skills_for_jobs(cleaned_df)
    logger.info(f"Extracted skills for {len(skills_df)} jobs")
    context["task_instance"].xcom_push(key="skills_jobs", value=skills_df)


# Task 5: Score jobs
def score_jobs_task(**context: Dict[str, Any]) -> None:
    """Calculate relevance scores for jobs"""
    logger.info("Starting job scoring task")

    skills_df = context["task_instance"].xcom_pull(
        task_ids="extract_skills", key="skills_jobs"
    )

    if skills_df is None or skills_df.empty:
        logger.warning("No jobs to score")
        return

    scored_df = score_jobs_from_dataframe(skills_df)
    logger.info(f"Scored {len(scored_df)} jobs")
    context["task_instance"].xcom_push(key="scored_jobs", value=scored_df)


# Task 6: Validate data quality
def validate_jobs_task(**context: Dict[str, Any]) -> None:
    """Validate data quality"""
    logger.info("Starting data validation task")

    scored_df = context["task_instance"].xcom_pull(
        task_ids="score_jobs", key="scored_jobs"
    )

    if scored_df is None or scored_df.empty:
        logger.warning("No jobs to validate")
        return

    validated_df, report = validate_dataframe(scored_df)
    logger.info(f"Validation report: {report}")
    context["task_instance"].xcom_push(key="validated_jobs", value=validated_df)
    context["task_instance"].xcom_push(key="validation_report", value=report)


# Task 7: Load cleaned and scored jobs to database
def load_cleaned_jobs_task(**context: Dict[str, Any]) -> None:
    """Load cleaned and scored jobs into cleaned_job_postings and related tables"""
    logger.info("Starting cleaned job load task")

    validated_df = context["task_instance"].xcom_pull(
        task_ids="validate_jobs", key="validated_jobs"
    )

    if validated_df is None or validated_df.empty:
        logger.warning("No validated jobs to load")
        return

    loader = DatabaseLoader()
    try:
        conn = loader.conn or loader.get_psycopg2_connection()
        cursor = conn.cursor()

        # Load cleaned jobs
        for idx, row in validated_df.iterrows():
            try:
                sql = """
                    INSERT INTO cleaned_job_postings (
                        raw_job_id, source_platform, title_clean, company_clean,
                        city, country, remote_type, employment_type, seniority_level,
                        salary_min, salary_max, salary_currency, posted_date,
                        scraped_date, job_url, description_clean, is_duplicate, is_active
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (job_url) DO NOTHING
                    RETURNING job_id
                """

                cursor.execute(
                    sql,
                    (
                        row.get("raw_job_id"),
                        row.get("source_platform"),
                        row.get("title_clean"),
                        row.get("company_clean"),
                        row.get("city"),
                        row.get("country", "Germany"),
                        row.get("remote_type"),
                        row.get("employment_type"),
                        row.get("seniority_level"),
                        row.get("salary_min"),
                        row.get("salary_max"),
                        row.get("salary_currency"),
                        row.get("posted_date"),
                        row.get("scraped_date"),
                        row.get("job_url"),
                        row.get("description_clean"),
                        row.get("is_duplicate", False),
                        True,
                    ),
                )

                result = cursor.fetchone()
                if result:
                    job_id = result[0]

                    # Insert match score
                    score_sql = """
                        INSERT INTO job_match_scores (
                            job_id, match_score, skill_match_count, matched_skills,
                            missing_skills, german_requirement, experience_requirement_min,
                            experience_requirement_max, priority_level
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (job_id) DO NOTHING
                    """

                    cursor.execute(
                        score_sql,
                        (
                            job_id,
                            row.get("match_score", 0),
                            row.get("skill_match_count", 0),
                            row.get("matched_skills", []),
                            row.get("missing_skills", []),
                            row.get("german_requirement", "None"),
                            row.get("exp_min"),
                            row.get("exp_max"),
                            row.get("priority_level", "Low"),
                        ),
                    )

                    # Insert skills
                    if isinstance(row.get("extracted_skills"), dict):
                        for category, skills in row["extracted_skills"].items():
                            for skill in skills:
                                skill_sql = """
                                    INSERT INTO job_skills (
                                        job_id, skill_name, skill_category
                                    ) VALUES (%s, %s, %s)
                                    ON CONFLICT (job_id, skill_name) DO NOTHING
                                """
                                cursor.execute(skill_sql, (job_id, skill, category))

            except Exception as e:
                logger.error(f"Error loading job at index {idx}: {e}")
                conn.rollback()
                continue

        conn.commit()
        logger.info(f"Loaded cleaned jobs and scores")

    finally:
        if cursor:
            cursor.close()
        loader.disconnect()


# Define tasks
extract_jobs = PythonOperator(
    task_id="extract_jobs",
    python_callable=extract_jobs_task,
    dag=dag,
)

load_raw_jobs = PythonOperator(
    task_id="load_raw_jobs",
    python_callable=load_raw_jobs_task,
    dag=dag,
)

clean_jobs = PythonOperator(
    task_id="clean_jobs",
    python_callable=clean_jobs_task,
    dag=dag,
)

extract_skills = PythonOperator(
    task_id="extract_skills",
    python_callable=extract_skills_task,
    dag=dag,
)

score_jobs = PythonOperator(
    task_id="score_jobs",
    python_callable=score_jobs_task,
    dag=dag,
)

validate_jobs = PythonOperator(
    task_id="validate_jobs",
    python_callable=validate_jobs_task,
    dag=dag,
)

load_cleaned_jobs = PythonOperator(
    task_id="load_cleaned_jobs",
    python_callable=load_cleaned_jobs_task,
    dag=dag,
)

# Set task dependencies
extract_jobs >> load_raw_jobs >> clean_jobs >> extract_skills >> score_jobs >> validate_jobs >> load_cleaned_jobs
