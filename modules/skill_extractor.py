"""Extract and compare skills using the project skills database."""

import re
from pathlib import Path

import pandas as pd


DEFAULT_SKILLS_FILE = Path("data/skills.csv")


def load_skills_database(
    file_path: Path = DEFAULT_SKILLS_FILE,
) -> list[str]:
    """Load unique skills from the skills CSV file."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"Skills database not found: {file_path}"
        )

    skills_dataframe = pd.read_csv(file_path)

    if "skill" not in skills_dataframe.columns:
        raise ValueError(
            "The skills database must contain a 'skill' column."
        )

    skills = (
        skills_dataframe["skill"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    skills = [
        skill
        for skill in skills
        if skill
    ]

    return list(dict.fromkeys(skills))


def skill_exists_in_text(skill: str, text: str) -> bool:
    """Check whether a complete skill term exists in text."""

    if not skill or not text:
        return False

    escaped_skill = re.escape(skill)

    pattern = rf"(?<!\w){escaped_skill}(?!\w)"

    return re.search(
        pattern,
        text,
        flags=re.IGNORECASE,
    ) is not None


def extract_skills(
    text: str,
    skills_database: list[str],
) -> list[str]:
    """Extract known skills from text without obvious partial matches."""

    if not text or not skills_database:
        return []

    detected_skills = [
        skill
        for skill in skills_database
        if skill_exists_in_text(skill, text)
    ]

    return detected_skills


def compare_skills(
    required_skills: list[str],
    candidate_skills: list[str],
) -> dict[str, object]:
    """Compare candidate skills with required skills."""

    required_lookup = {
        skill.lower(): skill
        for skill in required_skills
    }

    candidate_lookup = {
        skill.lower(): skill
        for skill in candidate_skills
    }

    matched_keys = (
        required_lookup.keys()
        & candidate_lookup.keys()
    )

    missing_keys = (
        required_lookup.keys()
        - candidate_lookup.keys()
    )

    additional_keys = (
        candidate_lookup.keys()
        - required_lookup.keys()
    )

    matched_skills = [
        required_lookup[key]
        for key in required_lookup
        if key in matched_keys
    ]

    missing_skills = [
        required_lookup[key]
        for key in required_lookup
        if key in missing_keys
    ]

    additional_skills = [
        candidate_lookup[key]
        for key in candidate_lookup
        if key in additional_keys
    ]

    if not required_lookup:
        skill_match_percentage = 0.0
    else:
        skill_match_percentage = (
            len(matched_skills)
            / len(required_lookup)
            * 100
        )

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "additional_skills": additional_skills,
        "skill_match_percentage": round(
            skill_match_percentage,
            2,
        ),
    }