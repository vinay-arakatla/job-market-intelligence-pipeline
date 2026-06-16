"""Data quality validation and checks"""

import pandas as pd

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DataValidator:
    """Validate data quality and integrity"""

    def __init__(self):
        """Initialize validator"""
        self.issues = []

    def validate_job_title(self, df: pd.DataFrame) -> tuple[pd.DataFrame, list]:
        """Validate job titles are not null

        Args:
            df: DataFrame to validate

        Returns:
            Tuple of (valid_df, null_titles)
        """
        null_titles = df[df["title_clean"].isna()]
        if not null_titles.empty:
            logger.warning(f"Found {len(null_titles)} jobs with null titles")
            self.issues.append(
                f"NULL job titles: {len(null_titles)} records removed"
            )

        return df[df["title_clean"].notna()].copy(), null_titles

    def validate_company(self, df: pd.DataFrame) -> tuple[pd.DataFrame, list]:
        """Validate company names are not null

        Args:
            df: DataFrame to validate

        Returns:
            Tuple of (valid_df, null_companies)
        """
        null_companies = df[df["company_clean"].isna()]
        if not null_companies.empty:
            logger.warning(f"Found {len(null_companies)} jobs with null company")
            self.issues.append(
                f"NULL company names: {len(null_companies)} records removed"
            )

        return df[df["company_clean"].notna()].copy(), null_companies

    def validate_job_url(self, df: pd.DataFrame) -> tuple[pd.DataFrame, list]:
        """Validate job URLs are not null

        Args:
            df: DataFrame to validate

        Returns:
            Tuple of (valid_df, null_urls)
        """
        null_urls = df[df["job_url"].isna()]
        if not null_urls.empty:
            logger.warning(f"Found {len(null_urls)} jobs with null URL")
            self.issues.append(f"NULL job URLs: {len(null_urls)} records removed")

        return df[df["job_url"].notna()].copy(), null_urls

    def validate_scraped_date(self, df: pd.DataFrame) -> tuple[pd.DataFrame, list]:
        """Validate scraped_date is populated

        Args:
            df: DataFrame to validate

        Returns:
            Tuple of (valid_df, null_dates)
        """
        null_dates = df[df["scraped_date"].isna()]
        if not null_dates.empty:
            logger.warning(f"Found {len(null_dates)} jobs with null scraped_date")
            self.issues.append(
                f"NULL scraped_date: {len(null_dates)} records removed"
            )

        return df[df["scraped_date"].notna()].copy(), null_dates

    def validate_match_score(self, df: pd.DataFrame) -> tuple[pd.DataFrame, list]:
        """Validate match_score is between 0 and 100

        Args:
            df: DataFrame to validate

        Returns:
            Tuple of (valid_df, invalid_scores)
        """
        if "match_score" not in df.columns:
            return df.copy(), []

        invalid_scores = df[
            (df["match_score"].isna())
            | (df["match_score"] < 0)
            | (df["match_score"] > 100)
        ]

        if not invalid_scores.empty:
            logger.warning(f"Found {len(invalid_scores)} jobs with invalid match_score")
            self.issues.append(
                f"Invalid match_score: {len(invalid_scores)} records removed"
            )

        return df[
            (df["match_score"].notna())
            & (df["match_score"] >= 0)
            & (df["match_score"] <= 100)
        ].copy(), invalid_scores

    def validate_salary_range(self, df: pd.DataFrame) -> tuple[pd.DataFrame, list]:
        """Validate salary_min <= salary_max

        Args:
            df: DataFrame to validate

        Returns:
            Tuple of (valid_df, invalid_salaries)
        """
        if "salary_min" not in df.columns or "salary_max" not in df.columns:
            return df.copy(), []

        # Only check rows where both salary values are present
        has_both_salaries = df[(df["salary_min"].notna()) & (df["salary_max"].notna())]

        if not has_both_salaries.empty:
            invalid_salaries = has_both_salaries[
                has_both_salaries["salary_min"] > has_both_salaries["salary_max"]
            ]

            if not invalid_salaries.empty:
                logger.warning(
                    f"Found {len(invalid_salaries)} jobs with invalid salary range"
                )
                self.issues.append(
                    f"Invalid salary range (min > max): {len(invalid_salaries)} records removed"
                )

                return df[
                    ~df.index.isin(invalid_salaries.index)
                    | (df["salary_min"].isna())
                    | (df["salary_max"].isna())
                ].copy(), invalid_salaries

        return df.copy(), []

    def validate_duplicates(
        self, df: pd.DataFrame
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Remove duplicate records

        Args:
            df: DataFrame to validate

        Returns:
            Tuple of (unique_df, duplicate_df)
        """
        duplicates = df[df["is_duplicate"] == True].copy()
        unique = df[df["is_duplicate"] != True].copy()

        if not duplicates.empty:
            logger.warning(f"Found {len(duplicates)} duplicate job records")
            self.issues.append(f"Duplicates removed: {len(duplicates)} records")

        return unique, duplicates

    def validate_all(self, df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
        """Run all validations

        Args:
            df: DataFrame to validate

        Returns:
            Tuple of (validated_df, validation_report)
        """
        logger.info(f"Starting data validation for {len(df)} records")

        initial_count = len(df)
        self.issues = []

        # Run validations sequentially
        df, _ = self.validate_job_title(df)
        df, _ = self.validate_company(df)
        df, _ = self.validate_job_url(df)
        df, _ = self.validate_scraped_date(df)
        df, _ = self.validate_salary_range(df)
        df, unique_df, dup_df = self.validate_duplicates(df)
        df, _ = self.validate_match_score(df)

        final_count = len(df)
        removed_count = initial_count - final_count

        report = {
            "initial_count": initial_count,
            "final_count": final_count,
            "removed_count": removed_count,
            "removal_percentage": (
                (removed_count / initial_count * 100) if initial_count > 0 else 0
            ),
            "issues": self.issues,
        }

        logger.info(
            f"Validation complete: {final_count} valid records, "
            f"{removed_count} removed ({report['removal_percentage']:.2f}%)"
        )
        logger.info(f"Issues: {self.issues}")

        return df, report

    def get_issue_summary(self) -> str:
        """Get summary of validation issues

        Returns:
            String summary of issues
        """
        return "\n".join(self.issues) if self.issues else "No issues found"


def validate_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Validate dataframe using DataValidator

    Args:
        df: DataFrame to validate

    Returns:
        Tuple of (validated_df, report)
    """
    validator = DataValidator()
    return validator.validate_all(df)


if __name__ == "__main__":
    # Test validation
    from datetime import datetime

    test_data = pd.DataFrame(
        {
            "title_clean": ["Data Analyst", None, "BI Analyst"],
            "company_clean": ["Tech Corp", "Data Inc", None],
            "job_url": ["http://example.com/1", None, "http://example.com/3"],
            "scraped_date": [datetime.now(), datetime.now(), None],
            "salary_min": [30000, 50000, 40000],
            "salary_max": [40000, 45000, 50000],  # Row 1 has invalid range
            "is_duplicate": [False, False, False],
            "match_score": [75, 110, -5],  # Row 1 and 2 invalid
        }
    )

    df_valid, report = validate_dataframe(test_data)

    logger.info(f"Validation report: {report}")
    logger.info(f"Validated data shape: {df_valid.shape}")
