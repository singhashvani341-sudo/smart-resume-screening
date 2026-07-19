"""Tests for the SQLite database module."""

import sqlite3

import pytest

from modules.database import (
    get_all_candidates,
    get_candidate_by_hash,
    initialize_database,
    save_candidate,
    clear_all_candidates,
)


def create_sample_candidate(
    file_hash: str = "test_hash_123",
    final_score: float = 80.0,
) -> dict[str, object]:
    """Create reusable sample candidate data."""

    return {
        "file_name": "resume.pdf",
        "file_hash": file_hash,
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+91 98765 43210",
        "experience": 3.0,
        "education": ["MBA"],
        "certifications": ["PMP"],
        "skills": ["Python", "SQL"],
        "matched_skills": ["Python"],
        "missing_skills": ["Power BI"],
        "similarity_score": 75.0,
        "skill_score": 50.0,
        "experience_score": 100.0,
        "education_score": 100.0,
        "certification_score": 100.0,
        "final_score": final_score,
    }


def test_initialize_database(tmp_path):
    """Database initialization must create the candidates table."""

    database_path = tmp_path / "test.db"

    initialize_database(str(database_path))

    with sqlite3.connect(database_path) as connection:
        result = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table' AND name = 'candidates'
            """
        ).fetchone()

    assert result is not None


def test_save_candidate(tmp_path):
    """A valid candidate must be saved successfully."""

    database_path = tmp_path / "test.db"
    initialize_database(str(database_path))

    candidate_id = save_candidate(
        create_sample_candidate(),
        str(database_path),
    )

    assert candidate_id == 1


def test_get_all_candidates(tmp_path):
    """Stored candidates must be retrieved."""

    database_path = tmp_path / "test.db"
    initialize_database(str(database_path))

    save_candidate(
        create_sample_candidate(),
        str(database_path),
    )

    candidates = get_all_candidates(str(database_path))

    assert len(candidates) == 1
    assert candidates[0]["name"] == "John Doe"
    assert candidates[0]["skills"] == ["Python", "SQL"]


def test_candidates_ordered_by_score(tmp_path):
    """Candidates must be returned from highest to lowest score."""

    database_path = tmp_path / "test.db"
    initialize_database(str(database_path))

    save_candidate(
        create_sample_candidate("hash_low", 60.0),
        str(database_path),
    )

    save_candidate(
        create_sample_candidate("hash_high", 90.0),
        str(database_path),
    )

    candidates = get_all_candidates(str(database_path))

    assert candidates[0]["final_score"] == 90.0
    assert candidates[1]["final_score"] == 60.0


def test_get_candidate_by_hash(tmp_path):
    """A candidate must be retrievable by file hash."""

    database_path = tmp_path / "test.db"
    initialize_database(str(database_path))

    save_candidate(
        create_sample_candidate(),
        str(database_path),
    )

    candidate = get_candidate_by_hash(
        "test_hash_123",
        str(database_path),
    )

    assert candidate is not None
    assert candidate["name"] == "John Doe"


def test_missing_candidate_hash(tmp_path):
    """An unknown file hash must return None."""

    database_path = tmp_path / "test.db"
    initialize_database(str(database_path))

    result = get_candidate_by_hash(
        "unknown_hash",
        str(database_path),
    )

    assert result is None


def test_duplicate_file_hash_allowed(tmp_path):
    """The same resume file must be allowed to be screened again."""

    database_path = tmp_path / "test.db"
    initialize_database(str(database_path))

    candidate = create_sample_candidate()

    first_candidate_id = save_candidate(
        candidate,
        str(database_path),
    )

    second_candidate_id = save_candidate(
        candidate,
        str(database_path),
    )

    candidates = get_all_candidates(str(database_path))

    assert first_candidate_id == 1
    assert second_candidate_id == 2
    assert len(candidates) == 2


def test_missing_required_field(tmp_path):
    """Missing required candidate fields must be rejected."""

    database_path = tmp_path / "test.db"
    initialize_database(str(database_path))

    candidate = create_sample_candidate()
    del candidate["name"]

    with pytest.raises(ValueError):
        save_candidate(candidate, str(database_path))

def test_clear_all_candidates(tmp_path):
    """All stored screening records must be deleted."""

    database_path = tmp_path / "test.db"
    initialize_database(str(database_path))

    candidate = create_sample_candidate()

    save_candidate(candidate, str(database_path))
    save_candidate(candidate, str(database_path))

    deleted_count = clear_all_candidates(
        str(database_path)
    )

    candidates = get_all_candidates(
        str(database_path)
    )

    assert deleted_count == 2
    assert candidates == []