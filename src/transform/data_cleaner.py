"""Data cleaning and transformation for job postings"""

import re
from typing import Optional, Tuple

import pandas as pd
import psycopg2

from src.utils.database import get_psycopg2_connection
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DataCleaner:
    """Clean and transform raw job data"""

    def __init__(self):
        """Initialize cleaner"""
        self.conn = None

    def clean_title(self, title: str) -> str:
        """Clean and normalize job title

        Args:
            title: Raw job title

        Returns:
            Cleaned title
        """
        if not title:
            return ""

        # Remove extra whitespace
        title = " ".join(title.split())

        # Standardize common terms
        replacements = {
            r"\bjunior\b": "Junior",
            r"\bsenior\b": "Senior",
            r"\blead\b": "Lead",
            r"\bdata\s+analyst\b": "Data Analyst",
            r"\bdata\s+engineer\b": "Data Engineer",
            r"\bbi\s+analyst\b": "BI Analyst",
            r"\bsql\s+developer\b": "SQL Developer",
        }

        for pattern, replacement in replacements.items():
            title = re.sub(pattern, replacement, title, flags=re.IGNORECASE)

        return title.title()

    def clean_company(self, company: str) -> str:
        """Clean and normalize company name

        Args:
            company: Raw company name

        Returns:
            Cleaned company name
        """
        if not company:
            return ""

        # Remove extra whitespace and special characters
        company = " ".join(company.split())
        company = re.sub(r"\s+", " ", company).strip()

        return company

    def parse_location(self, location: str) -> Tuple[Optional[str], str]:
        """Parse location into city and country

        Args:
            location: Raw location string

        Returns:
            Tuple of (city, country)
        """
        if not location:
            return None, "Germany"

        location_lower = location.lower()

        # Default to Germany for German cities or if "Germany" is mentioned
        country = "Germany"

        # Try to extract city
        city = location.split(",")[0].strip()

        # Common German cities
        german_cities = [
            "Berlin",
            "Munich",
            "Frankfurt",
            "Cologne",
            "Hamburg",
            "Stuttgart",
            "Dusseldorf",
            "Dortmund",
            "Leipzig",
            "Dresden",
        ]

        # Check if city matches
        for german_city in german_cities:
            if german_city.lower() in location_lower:
                city = german_city
                break

        return city, country

    def parse_remote_type(self, description: str, location: str) -> str:
        """Determine remote work type from description

        Args:
            description: Job description
            location: Job location

        Returns:
            Remote type: Remote, Hybrid, On-site
        """
        if not description:
            return "On-site"

        desc_lower = description.lower()

        if "remote" in desc_lower and "hybrid" in desc_lower:
            return "Hybrid"
        elif "fully remote" in desc_lower or "work from anywhere" in desc_lower:
            return "Remote"
        elif "remote" in desc_lower:
            return "Remote"
        elif "hybrid" in desc_lower:
            return "Hybrid"

        return "On-site"

    def parse_seniority_level(self, title: str, description: str) -> str:
        """Extract seniority level from title and description

        Args:
            title: Job title
            description: Job description

        Returns:
            Seniority level
        """
        combined_text = f"{title} {description}".lower()

        if "senior" in combined_text or "lead" in combined_text:
            return "Senior"
        elif "mid" in combined_text or "intermediate" in combined_text:
            return "Mid-level"
        elif (
            "junior" in combined_text
            or "entry" in combined_text
            or "intern" in combined_text
            or "graduate" in combined_text
        ):
            return "Junior"
        else:
            return "Not Specified"

    def parse_employment_type(self, job_type: Optional[str]) -> str:
        """Standardize employment type

        Args:
            job_type: Raw job type

        Returns:
            Standardized employment type
        """
        if not job_type:
            return "Full-time"

        job_type_lower = job_type.lower()

        if "full" in job_type_lower:
            return "Full-time"
        elif "part" in job_type_lower:
            return "Part-time"
        elif "contract" in job_type_lower or "freelance" in job_type_lower:
            return "Contract"
        elif "intern" in job_type_lower:
            return "Internship"
        elif "temporary" in job_type_lower:
            return "Temporary"
        else:
            return "Full-time"

    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean entire dataframe

        Args:
            df: Raw dataframe from database

        Returns:
            Cleaned dataframe
        """
        logger.info(f"Cleaning {len(df)} records")

        df_clean = df.copy()

        # Clean title
        df_clean["title_clean"] = df_clean["title"].apply(self.clean_title)

        # Clean company
        df_clean["company_clean"] = df_clean["company"].apply(self.clean_company)

        # Parse location
        df_clean[["city", "country"]] = df_clean["location"].apply(
            lambda x: pd.Series(self.parse_location(x))
        )

        # Parse remote type
        df_clean["remote_type"] = df_clean.apply(
            lambda row: self.parse_remote_type(
                row.get("description"), row.get("location", "")
            ),
            axis=1,
        )

        # Parse seniority level
        df_clean["seniority_level"] = df_clean.apply(
            lambda row: self.parse_seniority_level(
                row.get("title", ""), row.get("description", "")
            ),
            axis=1,
        )

        # Parse employment type
        df_clean["employment_type"] = df_clean["job_type"].apply(
            self.parse_employment_type
        )

        # Clean description
        df_clean["description_clean"] = df_clean["description"].fillna("")

        logger.info("Data cleaning complete")
        return df_clean

    def detect_duplicates(
        self, df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Detect duplicate jobs

        Args:
            df: Cleaned dataframe

        Returns:
            Tuple of (unique_jobs, duplicates)
        """
        logger.info(f"Detecting duplicates in {len(df)} records")

        # Mark duplicates based on title, company, location, and URL
        df["is_duplicate"] = df.duplicated(
            subset=["title_clean", "company_clean", "city", "job_url"],
            keep="first",
        )

        unique_jobs = df[~df["is_duplicate"]].copy()
        duplicates = df[df["is_duplicate"]].copy()

        logger.info(f"Found {len(duplicates)} duplicates, {len(unique_jobs)} unique")
        return unique_jobs, duplicates


def clean_raw_jobs() -> pd.DataFrame:
    """Load raw jobs, clean, and return dataframe"""
    try:
        conn = get_psycopg2_connection()
        query = "SELECT * FROM raw_job_postings WHERE is_active IS NULL OR is_active = TRUE LIMIT 1000"
        df = pd.read_sql_query(query, conn)
        conn.close()

        cleaner = DataCleaner()
        df_clean = cleaner.clean_dataframe(df)
        df_unique, df_dupes = cleaner.detect_duplicates(df_clean)

        logger.info(f"Cleaning complete: {len(df_unique)} unique jobs")
        return df_unique

    except Exception as e:
        logger.error(f"Error in cleaning pipeline: {e}")
        raise


if __name__ == "__main__":
    clean_raw_jobs()
