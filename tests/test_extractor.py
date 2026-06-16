"""Test suite for job extractor"""

import pytest
from unittest.mock import patch, MagicMock
import pandas as pd

from src.extract.jobspy_extractor import JobSpyExtractor


class TestJobSpyExtractor:
    """Tests for JobSpyExtractor"""

    def test_init(self):
        """Test extractor initialization"""
        extractor = JobSpyExtractor()
        assert extractor is not None
        assert len(extractor.jobs_data) == 0

    @patch("src.extract.jobspy_extractor.scrape_jobs")
    def test_extract_jobs_empty_result(self, mock_scrape):
        """Test extraction with empty results"""
        mock_scrape.return_value = pd.DataFrame()

        extractor = JobSpyExtractor()
        result = extractor.extract_jobs(
            job_titles=["Data Analyst"], locations=["Berlin"], platforms=["linkedin"]
        )

        assert result.empty

    def test_validate_extracted_data(self):
        """Test data validation"""
        test_df = pd.DataFrame(
            {
                "title": ["Data Analyst", None, "BI Analyst"],
                "company": ["Corp A", "Corp B", None],
                "job_url": ["http://example.com/1", None, "http://example.com/3"],
                "description": ["Desc 1", "Desc 2", "Desc 3"],
            }
        )

        extractor = JobSpyExtractor()
        validated = extractor.validate_extracted_data(test_df)

        # Should remove rows with null job_url
        assert len(validated) == 2
        assert "raw_data_json" in validated.columns

    def test_get_extracted_data(self):
        """Test getting extracted data"""
        test_df = pd.DataFrame({"title": ["Data Analyst"]})

        extractor = JobSpyExtractor()
        extractor.jobs_data = test_df
        result = extractor.get_extracted_data()

        assert len(result) == 1
        assert result["title"][0] == "Data Analyst"
