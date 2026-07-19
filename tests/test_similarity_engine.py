"""Tests for the AI/NLP similarity engine."""

from modules.similarity_engine import (
    calculate_multiple_similarities,
    calculate_similarity,
)


def test_identical_text():
    """Identical text must produce maximum similarity."""

    text = "Python SQL Power BI data analysis"

    result = calculate_similarity(text, text)

    assert result == 100.0


def test_unrelated_text():
    """Completely unrelated text must produce zero similarity."""

    result = calculate_similarity(
        "Python SQL data analysis",
        "cooking gardening photography",
    )

    assert result == 0.0


def test_partial_similarity():
    """Partially related text must produce a score between 0 and 100."""

    result = calculate_similarity(
        "Python SQL Power BI",
        "Python SQL Excel",
    )

    assert 0.0 < result < 100.0


def test_empty_job_description():
    """An empty job description must return zero."""

    result = calculate_similarity("", "Python SQL")

    assert result == 0.0


def test_empty_resume():
    """An empty resume must return zero."""

    result = calculate_similarity("Python SQL", "")

    assert result == 0.0


def test_very_short_text():
    """Very short valid text must be handled safely."""

    result = calculate_similarity("Python", "Python")

    assert result == 100.0


def test_empty_vocabulary():
    """Text containing only punctuation must return zero safely."""

    result = calculate_similarity("!!!", "@@@")

    assert result == 0.0


def test_multiple_resumes():
    """Multiple resumes must be processed independently."""

    results = calculate_multiple_similarities(
        "Python SQL",
        [
            "Python SQL",
            "Python",
            "Cooking gardening",
        ],
    )

    assert len(results) == 3
    assert results[0] == 100.0
    assert 0.0 < results[1] < 100.0
    assert results[2] == 0.0


def test_no_resumes():
    """An empty resume list must return an empty result."""

    result = calculate_multiple_similarities(
        "Python SQL",
        [],
    )

    assert result == []