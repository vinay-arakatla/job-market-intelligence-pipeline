"""Setup script for job market intelligence pipeline"""

import os
import sys
from pathlib import Path

from src.utils.config import get_settings
from src.utils.database import get_psycopg2_connection, execute_sql_file
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def create_directories() -> None:
    """Create necessary directories"""
    directories = [
        "data/raw",
        "data/processed",
        "logs",
        "airflow",
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")


def create_database_schema() -> None:
    """Create database schema by running SQL scripts"""
    settings = get_settings()

    try:
        conn = get_psycopg2_connection()
        logger.info("Connected to database")

        # SQL files to execute in order
        sql_files = [
            "sql/tables/raw_job_postings.sql",
            "sql/tables/cleaned_job_postings.sql",
            "sql/tables/job_skills.sql",
            "sql/tables/job_match_scores.sql",
            "sql/tables/applications_tracker.sql",
            "sql/views/dashboard_views.sql",
        ]

        for sql_file in sql_files:
            if os.path.exists(sql_file):
                logger.info(f"Executing: {sql_file}")
                execute_sql_file(sql_file, conn)
            else:
                logger.warning(f"SQL file not found: {sql_file}")

        conn.close()
        logger.info("Database schema created successfully")

    except Exception as e:
        logger.error(f"Error creating database schema: {e}")
        sys.exit(1)


def verify_environment() -> None:
    """Verify environment configuration"""
    logger.info("Verifying environment configuration...")

    settings = get_settings()

    # Check database settings
    if not settings.DB_HOST:
        logger.error("DB_HOST not configured")
        sys.exit(1)
    if not settings.DB_NAME:
        logger.error("DB_NAME not configured")
        sys.exit(1)

    logger.info(f"Database: {settings.DB_NAME} @ {settings.DB_HOST}:{settings.DB_PORT}")
    logger.info(f"Job titles: {', '.join(settings.JOB_TITLES[:3])}...")
    logger.info(f"Job locations: {', '.join(settings.JOB_LOCATIONS)}")
    logger.info(f"Platforms: {', '.join(settings.JOB_PLATFORMS)}")
    logger.info(f"Your skills: {', '.join(list(settings.PROFILE_SKILLS)[:5])}...")
    logger.info(f"German level: {settings.GERMAN_LEVEL}")
    logger.info(f"Years experience: {settings.YEARS_EXPERIENCE}")

    logger.info("Environment verification complete")


def setup() -> None:
    """Run complete setup"""
    logger.info("Starting setup...")

    # Step 1: Verify environment
    verify_environment()

    # Step 2: Create directories
    logger.info("Creating directories...")
    create_directories()

    # Step 3: Create database schema
    logger.info("Creating database schema...")
    create_database_schema()

    logger.info("✅ Setup complete!")
    logger.info("\nNext steps:")
    logger.info("1. Update .env with your database credentials if needed")
    logger.info("2. Run: python -c 'from src.extract.jobspy_extractor import main; main()'")
    logger.info("3. Setup Airflow: export AIRFLOW_HOME=$(pwd)/airflow && airflow db init")
    logger.info("4. View results in PowerBI/Tableau from SQL views")


if __name__ == "__main__":
    setup()
