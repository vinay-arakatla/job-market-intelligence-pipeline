"""JobSpy data extractor for job postings"""

import json
from datetime import datetime
from typing import List, Optional

import pandas as pd
from jobspy import scrape_jobs

from src.utils.config import get_settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class JobSpyExtractor:
    """Extract job postings using JobSpy library"""

    def __init__(self):
        """Initialize extractor with settings"""
        self.settings = get_settings()
        self.jobs_data = []

    def extract_jobs(
        self,
        job_titles: Optional[List[str]] = None,
        locations: Optional[List[str]] = None,
        platforms: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """Extract jobs using JobSpy

        Args:
            job_titles: List of job titles to search. Defaults to config.
            locations: List of locations to search. Defaults to config.
            platforms: List of job platforms. Defaults to config.

        Returns:
            DataFrame with extracted job data
        """
        job_titles = job_titles or self.settings.JOB_TITLES
        locations = locations or self.settings.JOB_LOCATIONS
        platforms = platforms or self.settings.JOB_PLATFORMS

        logger.info(
            f"Starting job extraction for {len(job_titles)} titles "
            f"in {len(locations)} locations from {len(platforms)} platforms"
        )

        all_jobs = []

        for job_title in job_titles:
            for location in locations:
                logger.info(f"Scraping: {job_title} in {location}")

                try:
                    jobs_df = scrape_jobs(
                        site_name=platforms,
                        search_term=job_title,
                        location=location,
                        results_wanted=self.settings.JOBSPY_MAX_RESULTS,
                        hours_old=24,  # Jobs posted in last 24 hours
                        timeout=self.settings.JOBSPY_TIMEOUT,
                    )

                    if jobs_df is not None and not jobs_df.empty:
                        # Add metadata columns
                        jobs_df["search_keyword"] = job_title
                        jobs_df["scraped_date"] = datetime.now()

                        all_jobs.append(jobs_df)
                        logger.info(
                            f"Found {len(jobs_df)} jobs for {job_title} in {location}"
                        )
                    else:
                        logger.warning(
                            f"No jobs found for {job_title} in {location}"
                        )

                except Exception as e:
                    logger.error(
                        f"Error scraping {job_title} in {location}: {str(e)}",
                        exc_info=True,
                    )
                    continue

        if all_jobs:
            combined_df = pd.concat(all_jobs, ignore_index=True)
            logger.info(f"Total jobs extracted: {len(combined_df)}")
            self.jobs_data = combined_df
            return combined_df
        else:
            logger.warning("No jobs were extracted")
            return pd.DataFrame()

    def validate_extracted_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate extracted data and handle missing values

        Args:
            df: DataFrame with extracted jobs

        Returns:
            Validated DataFrame
        """
        logger.info(f"Validating {len(df)} records")

        # Check required columns
        required_columns = ["title", "company", "job_url", "description"]
        missing_cols = [col for col in required_columns if col not in df.columns]

        if missing_cols:
            logger.warning(f"Missing columns: {missing_cols}")

        # Remove rows with null job_url (required for deduplication)
        df = df.dropna(subset=["job_url"])
        logger.info(f"Records after removing null URLs: {len(df)}")

        # Remove rows with null title or company
        df = df.dropna(subset=["title", "company"])
        logger.info(f"Records after removing null title/company: {len(df)}")

        # Add raw_data_json column with original data
        df["raw_data_json"] = df.apply(
            lambda row: json.dumps(row.to_dict(), default=str), axis=1
        )

        logger.info(f"Validation complete: {len(df)} valid records")
        return df

    def get_extracted_data(self) -> pd.DataFrame:
        """Get extracted data

        Returns:
            DataFrame with extracted jobs
        """
        return self.jobs_data


def main():
    """Run extractor standalone"""
    extractor = JobSpyExtractor()

    # Extract jobs
    jobs_df = extractor.extract_jobs()

    if not jobs_df.empty:
        # Validate
        jobs_df = extractor.validate_extracted_data(jobs_df)

        # Show summary
        logger.info(f"\n=== EXTRACTION SUMMARY ===")
        logger.info(f"Total jobs: {len(jobs_df)}")
        logger.info(f"Columns: {list(jobs_df.columns)}")
        logger.info(f"\nFirst few records:\n{jobs_df.head()}")

        return jobs_df
    else:
        logger.warning("No jobs extracted")
        return pd.DataFrame()


if __name__ == "__main__":
    main()
