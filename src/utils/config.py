"""Configuration management using environment variables"""

import os
from functools import lru_cache
from typing import List

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings from environment variables"""

    # Database Configuration
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", 5432))
    DB_NAME: str = os.getenv("DB_NAME", "job_market_db")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")

    # JobSpy Configuration
    JOBSPY_TIMEOUT: int = int(os.getenv("JOBSPY_TIMEOUT", 30))
    JOBSPY_MAX_RESULTS: int = int(os.getenv("JOBSPY_MAX_RESULTS", 500))

    # Pipeline Configuration
    PIPELINE_RUN_INTERVAL_DAYS: int = int(os.getenv("PIPELINE_RUN_INTERVAL_DAYS", 1))
    SCRAPE_BATCH_SIZE: int = int(os.getenv("SCRAPE_BATCH_SIZE", 100))

    # Job Search Configuration
    JOB_TITLES: List[str] = os.getenv(
        "JOB_TITLES",
        "Data Analyst,BI Analyst,Junior Data Engineer,SQL Developer,Power BI Analyst,Data Engineer Intern,Business Intelligence Developer",
    ).split(",")

    JOB_LOCATIONS: List[str] = os.getenv("JOB_LOCATIONS", "Berlin,Germany").split(",")

    JOB_PLATFORMS: List[str] = os.getenv(
        "JOB_PLATFORMS", "linkedin,indeed,glassdoor,google"
    ).split(",")

    # Profile Configuration
    PROFILE_SKILLS: List[str] = os.getenv(
        "PROFILE_SKILLS",
        "SQL,Python,Apache Airflow,PostgreSQL,Power BI,Tableau,ETL,Data Validation,Dashboarding,Reporting,Oracle Database,Spark",
    ).split(",")

    GERMAN_LEVEL: str = os.getenv("GERMAN_LEVEL", "B1")
    YEARS_EXPERIENCE: int = int(os.getenv("YEARS_EXPERIENCE", 3))

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/pipeline.log")

    # Development
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")

    @property
    def DATABASE_URL(self) -> str:
        """Construct database connection URL"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DATABASE_URL_PSYCOPG2(self) -> str:
        """Construct database connection string for psycopg2"""
        return f"dbname={self.DB_NAME} user={self.DB_USER} password={self.DB_PASSWORD} host={self.DB_HOST} port={self.DB_PORT}"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get application settings (cached)"""
    return Settings()
