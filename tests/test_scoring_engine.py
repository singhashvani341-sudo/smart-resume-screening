"""Tests for the final weighted scoring engine."""

import pytest

from config import SCORING_WEIGHTS
from modules.scoring_engine import (
    calculate_final_score,
    clamp_score,
    validate_scoring_weights,
)


def test_scoring_weights_are_valid():
    """Default scoring weights must be valid."""

    assert validate_scoring_weights(SCORING_WEIGHTS) is True


def test_weights_total_one():
    """Default scoring weights must total 1.0."""

    assert sum(SCORING_WEIGHTS.values()) == pytest.approx(1.0)


def test_perfect_final_score():
    """Perfect component scores must produce 100."""

    result = calculate_final_score(
        100,
        100,
        100,
        100,
        100,
    )

    assert result == 100.0


def test_zero_final_score():
    """Zero component scores must produce zero."""

    result = calculate_final_score(
        0,
        0,
        0,
        0,
        0,
    )

    assert result == 0.0


def test_weighted_final_score():
    """Component scores must use the configured weights."""

    result = calculate_final_score(
        similarity_score=80,
        skill_score=70,
        experience_score=60,
        education_score=100,
        certification_score=50,
    )

    assert result == 72.0


def test_score_above_100_is_clamped():
    """Scores above 100 must be clamped."""

    result = calculate_final_score(
        150,
        100,
        100,
        100,
        100,
    )

    assert result == 100.0


def test_negative_score_is_clamped():
    """Negative scores must be clamped."""

    result = calculate_final_score(
        -50,
        0,
        0,
        0,
        0,
    )

    assert result == 0.0


def test_invalid_component_score():
    """Invalid component scores must safely become zero."""

    result = calculate_final_score(
        "invalid",
        100,
        100,
        100,
        100,
    )

    assert result == 70.0


def test_invalid_weights_total():
    """Weights that do not total 1.0 must be rejected."""

    invalid_weights = {
        "similarity": 0.50,
        "skills": 0.50,
        "experience": 0.50,
        "education": 0.10,
        "certifications": 0.10,
    }

    with pytest.raises(ValueError):
        calculate_final_score(
            100,
            100,
            100,
            100,
            100,
            weights=invalid_weights,
        )


def test_missing_weight_component():
    """Missing scoring components must be rejected."""

    invalid_weights = {
        "similarity": 0.40,
        "skills": 0.30,
        "experience": 0.20,
        "education": 0.10,
    }

    assert validate_scoring_weights(invalid_weights) is False


def test_negative_weight():
    """Negative scoring weights must be rejected."""

    invalid_weights = {
        "similarity": 0.50,
        "skills": 0.30,
        "experience": 0.20,
        "education": 0.10,
        "certifications": -0.10,
    }

    assert validate_scoring_weights(invalid_weights) is False


def test_clamp_score():
    """Score clamping must handle valid and invalid values."""

    assert clamp_score(50) == 50.0
    assert clamp_score(150) == 100.0
    assert clamp_score(-20) == 0.0
    assert clamp_score("invalid") == 0.0