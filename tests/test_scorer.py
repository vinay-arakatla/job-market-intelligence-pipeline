"""Test suite for score calculator"""

import pytest

from src.scoring.score_calculator import ScoreCalculator


class TestScoreCalculator:
    """Tests for ScoreCalculator"""

    def test_init(self):
        """Test calculator initialization"""
        calculator = ScoreCalculator()
        assert calculator is not None
        assert len(calculator.user_skills) > 0

    def test_calculate_skill_match(self):
        """Test skill matching"""
        calculator = ScoreCalculator()

        job_skills = {
            "Programming": {"Python", "SQL"},
            "BI Tools": {"Power BI"},
        }

        match_count, matched, missing = calculator.calculate_skill_match(job_skills)

        assert match_count > 0
        assert len(matched) > 0

    def test_calculate_german_score(self):
        """Test German language scoring"""
        calculator = ScoreCalculator()

        # No requirement - should get bonus
        assert calculator.calculate_german_score("None") == 10

        # Meeting requirement
        assert calculator.calculate_german_score("B1") >= 0

        # C1/C2 requirement - should get penalty
        assert calculator.calculate_german_score("C1") == -30

    def test_calculate_experience_score(self):
        """Test experience scoring"""
        calculator = ScoreCalculator()

        # Perfect fit (3 years user experience)
        assert calculator.calculate_experience_score(2, 4) == 10

        # User overqualified
        assert calculator.calculate_experience_score(1, 2) > 0

    def test_calculate_seniority_score(self):
        """Test seniority level scoring"""
        calculator = ScoreCalculator()

        # Junior role - should get high score
        assert calculator.calculate_seniority_score("Junior") == 20

        # Senior role - should get lower score
        assert calculator.calculate_seniority_score("Senior") == -10

    def test_calculate_location_score(self):
        """Test location scoring"""
        calculator = ScoreCalculator()

        # Hybrid in Berlin - ideal
        assert calculator.calculate_location_score("Berlin", "Hybrid") == 15

        # Remote - good
        assert calculator.calculate_location_score("", "Remote") == 10

    def test_calculate_priority_level(self):
        """Test priority level determination"""
        calculator = ScoreCalculator()

        assert calculator.calculate_priority_level(85) == "High"
        assert calculator.calculate_priority_level(65) == "Medium"
        assert calculator.calculate_priority_level(40) == "Low"
