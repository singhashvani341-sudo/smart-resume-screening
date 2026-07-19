"""Tests for the skill extraction engine."""

from pathlib import Path

import pytest

from modules.skill_extractor import (
    compare_skills,
    extract_skills,
    load_skills_database,
    skill_exists_in_text,
)


def test_load_skills_database():
    """The real skills database must load successfully."""

    skills = load_skills_database()

    assert len(skills) == 70
    assert "Python" in skills
    assert "Power BI" in skills


def test_extract_skills():
    """Known skills must be extracted from text."""

    skills_database = ["Python", "SQL", "Power BI", "Java"]

    result = extract_skills(
        "Experienced in Python, SQL and Power BI.",
        skills_database,
    )

    assert result == ["Python", "SQL", "Power BI"]


def test_case_insensitive_matching():
    """Skill matching must ignore letter case."""

    result = extract_skills(
        "python and sql",
        ["Python", "SQL"],
    )

    assert result == ["Python", "SQL"]


def test_multi_word_skill():
    """Multi-word skills must be detected."""

    result = extract_skills(
        "Experienced in Project Management.",
        ["Project Management"],
    )

    assert result == ["Project Management"]


def test_prevent_partial_word_match():
    """A short skill must not match inside another word."""

    assert skill_exists_in_text("R", "Recruitment manager") is False


def test_empty_text():
    """Empty text must return no detected skills."""

    result = extract_skills("", ["Python", "SQL"])

    assert result == []


def test_compare_skills():
    """Required and candidate skills must be compared correctly."""

    result = compare_skills(
        required_skills=["Python", "SQL", "Power BI"],
        candidate_skills=["Python", "SQL", "Excel"],
    )

    assert result["matched_skills"] == ["Python", "SQL"]
    assert result["missing_skills"] == ["Power BI"]
    assert result["additional_skills"] == ["Excel"]
    assert result["skill_match_percentage"] == 66.67


def test_no_required_skills():
    """No required skills must not cause division by zero."""

    result = compare_skills(
        required_skills=[],
        candidate_skills=["Python"],
    )

    assert result["matched_skills"] == []
    assert result["missing_skills"] == []
    assert result["additional_skills"] == ["Python"]
    assert result["skill_match_percentage"] == 0.0


def test_missing_skills_database():
    """A missing skills database must raise a clear error."""

    missing_file = Path("data/file_that_does_not_exist.csv")

    with pytest.raises(FileNotFoundError):
        load_skills_database(missing_file)