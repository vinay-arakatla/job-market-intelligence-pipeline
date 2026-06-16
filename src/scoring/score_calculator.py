"""Calculate job match scores based on user profile"""

from typing import Dict, List, Set

import pandas as pd

from src.utils.config import get_settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ScoreCalculator:
    """Calculate job relevance scores based on user profile"""

    def __init__(self):
        """Initialize with user profile from settings"""
        self.settings = get_settings()
        self.user_skills = set(
            skill.strip().lower() for skill in self.settings.PROFILE_SKILLS
        )
        self.user_german_level = self.settings.GERMAN_LEVEL  # B1, B2, etc.
        self.user_experience = self.settings.YEARS_EXPERIENCE

        logger.info(f"Score calculator initialized with {len(self.user_skills)} skills")
        logger.info(f"German level: {self.user_german_level}")
        logger.info(f"Experience: {self.user_experience} years")

    def calculate_skill_match(
        self,
        job_skills: Dict[str, Set[str]],
        preferred_skills: Set[str] = None,
    ) -> tuple[int, List[str], List[str]]:
        """Calculate skill match count and get matched/missing skills

        Args:
            job_skills: Dictionary of skills found in job description
            preferred_skills: Skills that should be weighted higher

        Returns:
            Tuple of (match_count, matched_skills, missing_skills)
        """
        if preferred_skills is None:
            preferred_skills = {
                "sql",
                "python",
                "power bi",
                "apache airflow",
                "airflow",
                "postgresql",
                "etl",
            }

        # Flatten job skills
        job_skills_flat = set()
        for category, skills in job_skills.items():
            job_skills_flat.update(skill.lower() for skill in skills)

        # Calculate matches
        matched = []
        for user_skill in self.user_skills:
            for job_skill in job_skills_flat:
                if user_skill in job_skill or job_skill in user_skill:
                    matched.append(job_skill.title())
                    break

        # Remove duplicates and sort
        matched = list(set(matched))
        matched.sort()

        # Calculate missing skills
        missing = list(job_skills_flat - set(skill.lower() for skill in matched))
        missing.sort()

        match_count = len(matched)

        return match_count, matched, missing

    def calculate_german_score(self, job_german_level: str) -> int:
        """Calculate score based on German language requirement

        Args:
            job_german_level: German level required by job (None, A1, A2, B1, B2, C1, C2)

        Returns:
            Score adjustment (-30 to +10)
        """
        if job_german_level == "None" or not job_german_level:
            return 10  # +10 bonus for no German requirement

        job_level = job_german_level.upper()
        user_level = self.user_german_level.upper()

        # German level hierarchy
        levels = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5, "C2": 6}

        job_level_num = levels.get(job_level, 3)  # Default to B1
        user_level_num = levels.get(user_level, 3)

        # Scoring logic
        if user_level_num >= job_level_num:
            # User meets or exceeds requirement
            return 5
        elif user_level_num >= job_level_num - 1:
            # User is close to requirement (one level below)
            return 0
        elif job_level_num in [5, 6]:  # C1, C2
            # Job requires fluent German, user doesn't have it
            return -30
        else:
            # Lower penalty for lower level requirement not met
            return -10

    def calculate_experience_score(
        self, job_exp_min: int, job_exp_max: int
    ) -> int:
        """Calculate score based on experience requirement

        Args:
            job_exp_min: Minimum years of experience required
            job_exp_max: Maximum years of experience

        Returns:
            Score adjustment (-20 to +20)
        """
        if job_exp_min is None and job_exp_max is None:
            return 0  # No penalty if not specified

        # Handle None values
        min_exp = job_exp_min or 0
        max_exp = job_exp_max or min_exp + 5

        # Check if user fits in range
        if min_exp <= self.user_experience <= max_exp:
            return 10  # Perfect fit
        elif self.user_experience < min_exp:
            # User has less experience than required
            years_short = min_exp - self.user_experience
            if years_short <= 1:
                return 5  # Close to requirement
            elif years_short <= 2:
                return 0
            else:
                return -20  # Significant gap
        else:
            # User has more experience than max
            years_over = self.user_experience - max_exp
            if years_over <= 2:
                return 10  # Overqualification is OK
            else:
                return 5  # Might be seen as overqualified

    def calculate_seniority_score(self, seniority_level: str) -> int:
        """Calculate score based on seniority level

        Args:
            seniority_level: Job seniority level (Junior, Mid-level, Senior, etc.)

        Returns:
            Score adjustment (-10 to +20)
        """
        if not seniority_level:
            return 0

        seniority_lower = seniority_level.lower()

        # User profile: 3 years experience -> Mid-level
        # Prefer junior/entry-level, analyst, BI analyst, data engineer roles

        preferred_levels = [
            "junior",
            "entry",
            "intern",
            "trainee",
            "analyst",
            "bi analyst",
            "business intelligence",
        ]

        for level in preferred_levels:
            if level in seniority_lower:
                return 20  # High score for preferred levels

        if "mid" in seniority_lower or "intermediate" in seniority_lower:
            return 10  # Good fit
        elif "senior" in seniority_lower or "lead" in seniority_lower:
            return -10  # Lower score for senior roles
        else:
            return 0

    def calculate_location_score(
        self, city: str, remote_type: str
    ) -> int:
        """Calculate score based on location and remote work type

        Args:
            city: Job city
            remote_type: Remote, Hybrid, On-site

        Returns:
            Score adjustment (-10 to +15)
        """
        if not remote_type:
            return 0

        remote_lower = remote_type.lower()
        city_lower = (city or "").lower()

        # Preferred locations: Berlin, Remote Germany, Hybrid Berlin
        if remote_lower == "remote":
            return 10  # Fully remote is good
        elif remote_lower == "hybrid":
            if "berlin" in city_lower:
                return 15  # Hybrid in Berlin is ideal
            else:
                return 8  # Hybrid somewhere in Germany
        elif "berlin" in city_lower:
            return 12  # On-site in Berlin
        else:
            return 0  # Other German cities (neutral)

    def calculate_platform_score(self, source_platform: str) -> int:
        """Calculate score based on job platform

        Args:
            source_platform: Job source platform

        Returns:
            Score adjustment (-5 to +5)
        """
        # All platforms are treated equally
        return 0

    def calculate_employment_type_score(self, employment_type: str) -> int:
        """Calculate score based on employment type

        Args:
            employment_type: Full-time, Part-time, Contract, Internship

        Returns:
            Score adjustment (-5 to +5)
        """
        if not employment_type:
            return 0

        employment_lower = employment_type.lower()

        if "full" in employment_lower:
            return 5  # Prefer full-time
        elif "part" in employment_lower:
            return 0
        elif "contract" in employment_lower:
            return -5
        elif "intern" in employment_lower:
            return 10  # Internships preferred for junior
        else:
            return 0

    def calculate_title_match_score(self, job_title: str) -> int:
        """Calculate score based on job title match

        Args:
            job_title: Job title

        Returns:
            Score adjustment (-10 to +10)
        """
        if not job_title:
            return 0

        title_lower = job_title.lower()

        # Target titles
        high_priority_titles = [
            "data analyst",
            "bi analyst",
            "business intelligence analyst",
            "power bi analyst",
            "sql developer",
            "junior data engineer",
            "data engineer intern",
        ]

        for title in high_priority_titles:
            if title in title_lower:
                return 10  # Perfect match

        # Related titles
        if "data" in title_lower and "engineer" in title_lower:
            return 8
        elif "data" in title_lower and ("analyst" in title_lower or "bi" in title_lower):
            return 8
        elif "business" in title_lower and "intelligence" in title_lower:
            return 8
        elif "sql" in title_lower or "database" in title_lower:
            return 5
        elif "data" in title_lower:
            return 3
        else:
            return -10  # Not a data role

    def calculate_final_score(
        self,
        match_count: int,
        german_score: int,
        experience_score: int,
        seniority_score: int,
        location_score: int,
        employment_type_score: int,
        title_match_score: int,
    ) -> int:
        """Calculate final relevance score (0-100)

        Args:
            match_count: Number of matching skills
            german_score: German language score
            experience_score: Experience requirement score
            seniority_score: Seniority level score
            location_score: Location score
            employment_type_score: Employment type score
            title_match_score: Title match score

        Returns:
            Final score 0-100
        """
        # Base score from skill matches (max 50 points)
        # Each matched skill: 5 points (max 10 skills = 50 points)
        skill_score = min(match_count * 5, 50)

        # Component scores with weights
        total_score = (
            skill_score * 0.40  # 40% weight on skills
            + title_match_score * 0.15  # 15% weight on title
            + seniority_score * 0.15  # 15% weight on seniority
            + location_score * 0.15  # 15% weight on location
            + german_score * 0.10  # 10% weight on German
            + experience_score * 0.05  # 5% weight on experience
            + employment_type_score * 0.00  # 0% weight (bonus/malus only)
        )

        # Clamp to 0-100 range
        final_score = max(0, min(100, int(total_score)))

        return final_score

    def calculate_priority_level(self, score: int) -> str:
        """Determine priority level from score

        Args:
            score: Relevance score (0-100)

        Returns:
            Priority level: High, Medium, Low
        """
        if score >= 80:
            return "High"
        elif score >= 50:
            return "Medium"
        else:
            return "Low"

    def calculate_score_for_job(
        self,
        job_title: str,
        job_skills: Dict[str, Set[str]],
        german_requirement: str,
        experience_min: int,
        experience_max: int,
        seniority_level: str,
        city: str,
        remote_type: str,
        employment_type: str,
        source_platform: str,
    ) -> tuple[int, str, int, List[str], List[str]]:
        """Calculate complete score for a job

        Args:
            job_title: Job title
            job_skills: Extracted skills dictionary
            german_requirement: German level required
            experience_min: Minimum experience required
            experience_max: Maximum experience
            seniority_level: Job seniority level
            city: Job city
            remote_type: Remote work type
            employment_type: Employment type
            source_platform: Job platform

        Returns:
            Tuple of (score, priority, skill_match_count, matched_skills, missing_skills)
        """
        # Calculate individual components
        match_count, matched_skills, missing_skills = self.calculate_skill_match(
            job_skills
        )
        german_score = self.calculate_german_score(german_requirement)
        experience_score = self.calculate_experience_score(experience_min, experience_max)
        seniority_score = self.calculate_seniority_score(seniority_level)
        location_score = self.calculate_location_score(city, remote_type)
        employment_type_score = self.calculate_employment_type_score(employment_type)
        title_match_score = self.calculate_title_match_score(job_title)

        # Calculate final score
        final_score = self.calculate_final_score(
            match_count,
            german_score,
            experience_score,
            seniority_score,
            location_score,
            employment_type_score,
            title_match_score,
        )

        # Determine priority
        priority = self.calculate_priority_level(final_score)

        logger.debug(
            f"Score breakdown for {job_title}: "
            f"skills={skill_score}, title={title_match_score}, "
            f"seniority={seniority_score}, location={location_score}, "
            f"german={german_score}, exp={experience_score}"
        )

        return final_score, priority, match_count, matched_skills, missing_skills


def score_jobs_from_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Score all jobs in a dataframe

    Args:
        df: Dataframe with job data and extracted skills

    Returns:
        Modified dataframe with score columns added
    """
    calculator = ScoreCalculator()
    logger.info(f"Scoring {len(df)} jobs")

    scores = []
    priorities = []
    match_counts = []
    matched_skills_list = []
    missing_skills_list = []

    for idx, row in df.iterrows():
        try:
            score, priority, match_count, matched, missing = (
                calculator.calculate_score_for_job(
                    job_title=row.get("title_clean", ""),
                    job_skills=row.get("extracted_skills", {}),
                    german_requirement=row.get("german_requirement", "None"),
                    experience_min=row.get("exp_min"),
                    experience_max=row.get("exp_max"),
                    seniority_level=row.get("seniority_level", ""),
                    city=row.get("city", ""),
                    remote_type=row.get("remote_type", "On-site"),
                    employment_type=row.get("employment_type", "Full-time"),
                    source_platform=row.get("source_platform", ""),
                )
            )
            scores.append(score)
            priorities.append(priority)
            match_counts.append(match_count)
            matched_skills_list.append(matched)
            missing_skills_list.append(missing)
        except Exception as e:
            logger.error(f"Error scoring job at index {idx}: {e}")
            scores.append(0)
            priorities.append("Low")
            match_counts.append(0)
            matched_skills_list.append([])
            missing_skills_list.append([])

    df["match_score"] = scores
    df["priority_level"] = priorities
    df["skill_match_count"] = match_counts
    df["matched_skills"] = matched_skills_list
    df["missing_skills"] = missing_skills_list

    logger.info(
        f"Scoring complete. High: {sum(1 for p in priorities if p == 'High')}, "
        f"Medium: {sum(1 for p in priorities if p == 'Medium')}, "
        f"Low: {sum(1 for p in priorities if p == 'Low')}"
    )

    return df


if __name__ == "__main__":
    # Test scoring
    calculator = ScoreCalculator()

    test_job = {
        "title_clean": "Junior Data Analyst",
        "extracted_skills": {
            "Programming": {"Python", "SQL"},
            "BI Tools": {"Power BI"},
            "Data Engineering": {"ETL"},
        },
        "german_requirement": "B1",
        "exp_min": 1,
        "exp_max": 3,
        "seniority_level": "Junior",
        "city": "Berlin",
        "remote_type": "Hybrid",
        "employment_type": "Full-time",
        "source_platform": "linkedin",
    }

    score, priority, match_count, matched, missing = calculator.calculate_score_for_job(
        **test_job
    )

    logger.info(f"Test score: {score}, Priority: {priority}")
    logger.info(f"Matched: {matched}, Missing: {missing}")
