"""Rank candidates using their final screening scores."""


def rank_candidates(
    candidates: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Rank candidates from highest to lowest final score."""

    if not candidates:
        return []

    ranked_candidates = []

    for candidate in candidates:
        candidate_copy = candidate.copy()

        try:
            final_score = float(
                candidate_copy.get("final_score", 0.0)
            )
        except (TypeError, ValueError):
            final_score = 0.0

        final_score = max(0.0, min(100.0, final_score))
        candidate_copy["final_score"] = round(final_score, 2)

        ranked_candidates.append(candidate_copy)

    ranked_candidates.sort(
        key=lambda candidate: candidate["final_score"],
        reverse=True,
    )

    for rank, candidate in enumerate(
        ranked_candidates,
        start=1,
    ):
        candidate["rank"] = rank

    return ranked_candidates