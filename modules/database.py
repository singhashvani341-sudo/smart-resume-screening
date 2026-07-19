"""Store and retrieve resume screening results using SQLite."""

import json
import sqlite3
from pathlib import Path
from typing import Optional

from config import DATABASE_PATH


def get_database_connection(
    database_path: str = DATABASE_PATH,
) -> sqlite3.Connection:
    """Create a SQLite database connection."""

    database_file = Path(database_path)
    database_file.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(database_file)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database(
    database_path: str = DATABASE_PATH,
) -> None:
    """Create the candidates table if it does not already exist."""

    with get_database_connection(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                experience REAL,
                education TEXT NOT NULL,
                certifications TEXT NOT NULL,
                skills TEXT NOT NULL,
                matched_skills TEXT NOT NULL,
                missing_skills TEXT NOT NULL,
                similarity_score REAL NOT NULL,
                skill_score REAL NOT NULL,
                experience_score REAL NOT NULL,
                education_score REAL NOT NULL,
                certification_score REAL NOT NULL,
                final_score REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def save_candidate(
    candidate: dict[str, object],
    database_path: str = DATABASE_PATH,
) -> int:
    """Save one candidate and return the new database record ID."""

    required_fields = {
        "file_name",
        "file_hash",
        "name",
        "email",
        "phone",
        "education",
        "certifications",
        "skills",
        "matched_skills",
        "missing_skills",
        "similarity_score",
        "skill_score",
        "experience_score",
        "education_score",
        "certification_score",
        "final_score",
    }

    missing_fields = required_fields - candidate.keys()

    if missing_fields:
        raise ValueError(
            "Missing required candidate fields: "
            + ", ".join(sorted(missing_fields))
        )

    with get_database_connection(database_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO candidates (
                file_name,
                file_hash,
                name,
                email,
                phone,
                experience,
                education,
                certifications,
                skills,
                matched_skills,
                missing_skills,
                similarity_score,
                skill_score,
                experience_score,
                education_score,
                certification_score,
                final_score
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                candidate["file_name"],
                candidate["file_hash"],
                candidate["name"],
                candidate["email"],
                candidate["phone"],
                candidate.get("experience"),
                json.dumps(candidate["education"]),
                json.dumps(candidate["certifications"]),
                json.dumps(candidate["skills"]),
                json.dumps(candidate["matched_skills"]),
                json.dumps(candidate["missing_skills"]),
                candidate["similarity_score"],
                candidate["skill_score"],
                candidate["experience_score"],
                candidate["education_score"],
                candidate["certification_score"],
                candidate["final_score"],
            ),
        )

        return cursor.lastrowid


def get_all_candidates(
    database_path: str = DATABASE_PATH,
) -> list[dict[str, object]]:
    """Return all stored candidates."""

    with get_database_connection(database_path) as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM candidates
            ORDER BY final_score DESC, id ASC
            """
        ).fetchall()

    candidates = []

    for row in rows:
        candidate = dict(row)

        for field in (
            "education",
            "certifications",
            "skills",
            "matched_skills",
            "missing_skills",
        ):
            candidate[field] = json.loads(candidate[field])

        candidates.append(candidate)

    return candidates


def get_candidate_by_hash(
    file_hash: str,
    database_path: str = DATABASE_PATH,
) -> Optional[dict[str, object]]:
    """Return a candidate matching the supplied file hash."""

    with get_database_connection(database_path) as connection:
        row = connection.execute(
            """
            SELECT *
            FROM candidates
            WHERE file_hash = ?
            """,
            (file_hash,),
        ).fetchone()

    if row is None:
        return None

    candidate = dict(row)

    for field in (
        "education",
        "certifications",
        "skills",
        "matched_skills",
        "missing_skills",
    ):
        candidate[field] = json.loads(candidate[field])

    return candidate


def clear_all_candidates(
    database_path: str = DATABASE_PATH,
) -> int:
    """Delete all stored candidate screening records."""

    initialize_database(database_path)

    with sqlite3.connect(database_path) as connection:
        cursor = connection.execute(
            "DELETE FROM candidates"
        )

        deleted_count = cursor.rowcount

        connection.commit()

    return deleted_count

def clear_all_candidates(
    database_path: str = DATABASE_PATH,
) -> int:
    """Delete all stored candidate screening records."""

    initialize_database(database_path)

    with sqlite3.connect(database_path) as connection:
        cursor = connection.execute(
            "DELETE FROM candidates"
        )

        deleted_count = cursor.rowcount

        connection.commit()

    return deleted_count