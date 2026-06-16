"""Test suite for data cleaner"""

import pytest
from datetime import datetime

from src.transform.data_cleaner import DataCleaner


class TestDataCleaner:
    """Tests for DataCleaner"""

    def test_clean_title(self):
        """Test title cleaning"""
        cleaner = DataCleaner()

        assert cleaner.clean_title("  data   analyst  ") == "Data Analyst"
        assert cleaner.clean_title("JUNIOR data engineer") == "Junior Data Engineer"
        assert cleaner.clean_title("senior bi analyst") == "Senior Bi Analyst"

    def test_clean_company(self):
        """Test company name cleaning"""
        cleaner = DataCleaner()

        assert cleaner.clean_company("  Tech  Corp  ") == "Tech Corp"
        assert cleaner.clean_company("Data Inc.") == "Data Inc."

    def test_parse_location(self):
        """Test location parsing"""
        cleaner = DataCleaner()

        city, country = cleaner.parse_location("Berlin, Germany")
        assert city == "Berlin"
        assert country == "Germany"

        city, country = cleaner.parse_location("Munich")
        assert city == "Munich"
        assert country == "Germany"

    def test_parse_remote_type(self):
        """Test remote type detection"""
        cleaner = DataCleaner()

        assert cleaner.parse_remote_type("Fully remote position", "") == "Remote"
        assert cleaner.parse_remote_type("Hybrid role", "") == "Hybrid"
        assert cleaner.parse_remote_type("On-site only", "") == "On-site"
        assert cleaner.parse_remote_type("", "") == "On-site"

    def test_parse_seniority_level(self):
        """Test seniority level extraction"""
        cleaner = DataCleaner()

        assert cleaner.parse_seniority_level("Junior Data Analyst", "") == "Junior"
        assert cleaner.parse_seniority_level("Senior Data Engineer", "") == "Senior"
        assert cleaner.parse_seniority_level(
            "Data Analyst", "Mid-level position with 3-5 years experience"
        ) == "Mid-level"

    def test_parse_employment_type(self):
        """Test employment type parsing"""
        cleaner = DataCleaner()

        assert cleaner.parse_employment_type("Full-time") == "Full-time"
        assert cleaner.parse_employment_type("Part-time") == "Part-time"
        assert cleaner.parse_employment_type("Contract") == "Contract"
        assert cleaner.parse_employment_type("Internship") == "Internship"
