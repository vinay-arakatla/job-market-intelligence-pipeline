"""Load extracted data into PostgreSQL database"""

from datetime import datetime
from typing import List, Optional

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

from src.utils.config import get_settings
from src.utils.database import get_psycopg2_connection
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DatabaseLoader:
    """Load data into PostgreSQL database"""

    def __init__(self):
        """Initialize loader"""
        self.settings = get_settings()
        self.conn = None

    def connect(self) -> None:
        """Establish database connection"""
        try:
            self.conn = get_psycopg2_connection()
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def disconnect(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def load_raw_jobs(
        self, df: pd.DataFrame, batch_size: int = 100
    ) -> tuple[int, int]:
        """Load raw job data into raw_job_postings table

        Args:
            df: DataFrame with extracted jobs
            batch_size: Number of records to insert per batch

        Returns:
            Tuple of (inserted_count, skipped_count)
        """
        if not self.conn:
            self.connect()

        if df.empty:
            logger.warning("Empty DataFrame provided")
            return 0, 0

        logger.info(f"Loading {len(df)} raw job records into database")

        inserted_count = 0
        skipped_count = 0
        cursor = self.conn.cursor()

        try:
            for idx, row in df.iterrows():
                try:
                    # Prepare data
                    sql = """
                        INSERT INTO raw_job_postings (
                            source_platform, search_keyword, title, company, location,
                            job_type, job_level, salary_min, salary_max, salary_currency,
                            salary_interval, posted_date, scraped_date, job_url, company_url,
                            description, raw_data_json
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (job_url) DO NOTHING
                    """

                    values = (
                        row.get("site_name", "unknown"),
                        row.get("search_keyword", ""),
                        row.get("title"),
                        row.get("company"),
                        row.get("location"),
                        row.get("job_type"),
                        row.get("job_level"),
                        row.get("min_amount"),
                        row.get("max_amount"),
                        row.get("currency"),
                        row.get("salary_interval"),
                        row.get("date_posted"),
                        row.get("scraped_date", datetime.now()),
                        row.get("job_url"),
                        row.get("company_url"),
                        row.get("description"),
                        row.get("raw_data_json"),
                    )

                    cursor.execute(sql, values)
                    inserted_count += 1

                    # Commit in batches
                    if (idx + 1) % batch_size == 0:
                        self.conn.commit()
                        logger.info(f"Committed batch at record {idx + 1}")

                except psycopg2.IntegrityError:
                    # Duplicate entry, skip
                    skipped_count += 1
                    self.conn.rollback()
                except Exception as e:
                    logger.error(f"Error inserting row {idx}: {e}")
                    skipped_count += 1
                    self.conn.rollback()

            # Final commit
            self.conn.commit()
            logger.info(
                f"Raw jobs loading complete: {inserted_count} inserted, {skipped_count} skipped"
            )

        except Exception as e:
            logger.error(f"Error loading raw jobs: {e}")
            self.conn.rollback()
            raise
        finally:
            cursor.close()

        return inserted_count, skipped_count

    def execute_query(self, query: str, params: Optional[tuple] = None) -> list:
        """Execute a SELECT query

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            List of results
        """
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        finally:
            cursor.close()

    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """Execute an INSERT/UPDATE/DELETE query

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Number of affected rows
        """
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()
        try:
            cursor.execute(query, params or ())
            self.conn.commit()
            return cursor.rowcount
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error executing update: {e}")
            raise
        finally:
            cursor.close()


def main():
    """Test database loader"""
    # Create sample data
    sample_data = pd.DataFrame(
        {
            "site_name": ["linkedin", "indeed"],
            "search_keyword": ["Data Analyst", "Data Analyst"],
            "title": ["Data Analyst", "Senior Data Analyst"],
            "company": ["Tech Corp", "Data Inc"],
            "location": ["Berlin", "Germany"],
            "job_type": ["Full-time", "Full-time"],
            "job_level": ["Entry-level", "Mid-level"],
            "min_amount": [30000, 50000],
            "max_amount": [40000, 70000],
            "currency": ["EUR", "EUR"],
            "salary_interval": ["yearly", "yearly"],
            "date_posted": [datetime.now(), datetime.now()],
            "scraped_date": [datetime.now(), datetime.now()],
            "job_url": ["http://example.com/job1", "http://example.com/job2"],
            "company_url": ["http://techcorp.com", "http://datainc.com"],
            "description": ["Job description 1", "Job description 2"],
            "raw_data_json": ["{}", "{}"],
        }
    )

    loader = DatabaseLoader()
    try:
        inserted, skipped = loader.load_raw_jobs(sample_data)
        logger.info(f"Test load: {inserted} inserted, {skipped} skipped")
    finally:
        loader.disconnect()


if __name__ == "__main__":
    main()
