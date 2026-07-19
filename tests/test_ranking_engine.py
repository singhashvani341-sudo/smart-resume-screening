"""Tests for the candidate ranking engine."""

from modules.ranking_engine import rank_candidates


def test_rank_candidates():
    """Candidates must be ranked from highest to lowest score."""

    candidates = [
        {"name": "Candidate A", "final_score": 70},
        {"name": "Candidate B", "final_score": 90},
        {"name": "Candidate C", "final_score": 80},
    ]

    result = rank_candidates(candidates)

    assert result[0]["name"] == "Candidate B"
    assert result[1]["name"] == "Candidate C"
    assert result[2]["name"] == "Candidate A"


def test_rank_numbers():
    """Sequential rank numbers must be assigned."""

    candidates = [
        {"name": "Candidate A", "final_score": 60},
        {"name": "Candidate B", "final_score": 90},
    ]

    result = rank_candidates(candidates)

    assert result[0]["rank"] == 1
    assert result[1]["rank"] == 2


def test_empty_candidate_list():
    """An empty candidate list must return an empty list."""

    assert rank_candidates([]) == []


def test_missing_final_score():
    """A missing final score must safely become zero."""

    candidates = [
        {"name": "Candidate A"},
        {"name": "Candidate B", "final_score": 50},
    ]

    result = rank_candidates(candidates)

    assert result[0]["name"] == "Candidate B"
    assert result[1]["final_score"] == 0.0


def test_invalid_final_score():
    """An invalid final score must safely become zero."""

    candidates = [
        {"name": "Candidate A", "final_score": "invalid"},
    ]

    result = rank_candidates(candidates)

    assert result[0]["final_score"] == 0.0


def test_score_above_100():
    """A score above 100 must be clamped."""

    candidates = [
        {"name": "Candidate A", "final_score": 150},
    ]

    result = rank_candidates(candidates)

    assert result[0]["final_score"] == 100.0


def test_negative_score():
    """A negative score must be clamped."""

    candidates = [
        {"name": "Candidate A", "final_score": -20},
    ]

    result = rank_candidates(candidates)

    assert result[0]["final_score"] == 0.0


def test_original_data_not_modified():
    """Ranking must not modify the original candidate dictionaries."""

    candidates = [
        {"name": "Candidate A", "final_score": 80},
    ]

    rank_candidates(candidates)

    assert "rank" not in candidates[0]