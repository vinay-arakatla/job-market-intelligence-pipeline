"""Extract skills from job descriptions"""

import re
from typing import Dict, List, Set

import pandas as pd

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# Skill definitions by category
SKILL_CATEGORIES = {
    "Programming": {
        "Python",
        "SQL",
        "Java",
        "Scala",
        "R",
        "JavaScript",
        "C++",
        "C#",
        "PHP",
        "Kotlin",
    },
    "BI Tools": {
        "Power BI",
        "Tableau",
        "Looker",
        "Qlik",
        "Microstrategy",
        "SSRS",
        "Metabase",
    },
    "Data Engineering": {
        "Apache Airflow",
        "Airflow",
        "Apache Spark",
        "Spark",
        "Kafka",
        "dbt",
        "ETL",
        "Data Pipeline",
        "PostgreSQL",
        "MySQL",
        "MongoDB",
        "Snowflake",
        "BigQuery",
        "Redshift",
    },
    "Cloud": {"AWS", "Azure", "GCP", "Google Cloud", "Databricks", "Snowflake"},
    "German Language": {
        "German",
        "Deutsch",
        "B1",
        "B2",
        "C1",
        "C2",
        "Fluent",
        "Native",
        "Fließend",
    },
    "Analytics": {
        "Excel",
        "Analytics",
        "Reporting",
        "Dashboarding",
        "KPI",
        "Data Analysis",
        "Statistical Analysis",
        "A/B Testing",
    },
}


class SkillExtractor:
    """Extract skills from job descriptions"""

    def __init__(self):
        """Initialize extractor with skill categories"""
        self.skill_categories = SKILL_CATEGORIES
        self.all_skills = {skill for skills in SKILL_CATEGORIES.values() for skill in skills}

    def extract_skills(self, text: str) -> Dict[str, Set[str]]:
        """Extract skills from text

        Args:
            text: Job description text

        Returns:
            Dictionary mapping category to set of found skills
        """
        if not text:
            return {}

        text_lower = text.lower()
        found_skills = {}

        for category, skills in self.skill_categories.items():
            found_in_category = set()

            for skill in skills:
                skill_pattern = r"\b" + re.escape(skill.lower()) + r"\b"
                if re.search(skill_pattern, text_lower):
                    found_in_category.add(skill)

            if found_in_category:
                found_skills[category] = found_in_category

        return found_skills

    def extract_german_level(self, text: str) -> str:
        """Extract German language level requirement from text

        Args:
            text: Job description text

        Returns:
            German level: None, A1, A2, B1, B2, C1, C2
        """
        if not text:
            return "None"

        text_lower = text.lower()

        # Check in order from highest to lowest level
        levels = ["c2", "c1", "b2", "b1", "a2", "a1"]
        for level in levels:
            if re.search(r"\b" + level + r"\b", text_lower):
                return level.upper()

        # Check for fluent German requirement
        if re.search(r"fluent|native|flie[ßs]end|deutsch", text_lower):
            return "B2"  # Assume B2+ for fluent

        return "None"

    def extract_experience_requirement(
        self, text: str
    ) -> tuple[int, int]:
        """Extract years of experience requirement from text

        Args:
            text: Job description text

        Returns:
            Tuple of (min_years, max_years)
        """
        if not text:
            return None, None

        text_lower = text.lower()

        # Look for patterns like "3+ years", "3-5 years", "5 years experience"
        patterns = [
            r"(\d+)\s*-\s*(\d+)\s+years?",  # 3-5 years
            r"(\d+)\+\s+years?",  # 3+ years
            r"(\d+)\s+years?\s+of\s+experience",  # 3 years of experience
        ]

        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                groups = match.groups()
                if len(groups) == 2:
                    return int(groups[0]), int(groups[1])
                elif len(groups) == 1:
                    years = int(groups[0])
                    return years, years + 2  # Assume range of +2 years

        return None, None

    def flatten_skills_to_list(
        self, skills_dict: Dict[str, Set[str]]
    ) -> tuple[List[str], List[str]]:
        """Flatten skill dictionary to lists by category

        Args:
            skills_dict: Dictionary mapping category to skills

        Returns:
            Tuple of (category_list, skill_list)
        """
        categories = []
        skills = []

        for category, skill_set in skills_dict.items():
            for skill in skill_set:
                categories.append(category)
                skills.append(skill)

        return categories, skills


def extract_skills_for_jobs(df: pd.DataFrame) -> pd.DataFrame:
    """Extract skills for all jobs in dataframe

        Args:
            df: Dataframe with job descriptions

        Returns:
            Modified dataframe with skills extracted
        """
    extractor = SkillExtractor()
    logger.info(f"Extracting skills from {len(df)} jobs")

    # Create new columns for skills
    df["extracted_skills"] = df["description_clean"].apply(
        lambda x: extractor.extract_skills(x)
    )

    # Extract German level
    df["german_requirement"] = df["description_clean"].apply(
        lambda x: extractor.extract_german_level(x)
    )

    # Extract experience requirement
    df[["exp_min", "exp_max"]] = df["description_clean"].apply(
        lambda x: pd.Series(extractor.extract_experience_requirement(x))
    )

    logger.info("Skill extraction complete")
    return df


if __name__ == "__main__":
    # Test
    extractor = SkillExtractor()
    test_text = """
    We are looking for a Data Analyst with Python and SQL skills.
    Experience with Power BI and Tableau is required.
    Must have 3-5 years of experience in data analysis.
    German language B2 level required.
    Strong knowledge of ETL pipelines and Apache Airflow.
    """

    skills = extractor.extract_skills(test_text)
    logger.info(f"Extracted skills: {skills}")
    logger.info(f"German level: {extractor.extract_german_level(test_text)}")
    logger.info(
        f"Experience: {extractor.extract_experience_requirement(test_text)} years"
    )
