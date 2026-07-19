"""Calculate the final weighted candidate score."""

from config import SCORING_WEIGHTS


def clamp_score(score: float) -> float:
    """Keep a score within the valid 0 to 100 range."""

    try:
        score = float(score)
    except (TypeError, ValueError):
        return 0.0

    return max(0.0, min(100.0, score))


def validate_scoring_weights(
    weights: dict[str, float],
) -> bool:
    """Check whether scoring weights are complete and total 1.0."""

    required_components = {
        "similarity",
        "skills",
        "experience",
        "education",
        "certifications",
    }

    if set(weights.keys()) != required_components:
        return False

    try:
        numeric_weights = [
            float(weight)
            for weight in weights.values()
        ]
    except (TypeError, ValueError):
        return False

    if any(weight < 0 for weight in numeric_weights):
        return False

    return abs(sum(numeric_weights) - 1.0) < 1e-9


def calculate_final_score(
    similarity_score: float,
    skill_score: float,
    experience_score: float,
    education_score: float,
    certification_score: float,
    weights: dict[str, float] = SCORING_WEIGHTS,
) -> float:
    """Calculate the final weighted score on a 0 to 100 scale."""

    if not validate_scoring_weights(weights):
        raise ValueError(
            "Scoring weights are invalid or do not total 1.0."
        )

    component_scores = {
        "similarity": clamp_score(similarity_score),
        "skills": clamp_score(skill_score),
        "experience": clamp_score(experience_score),
        "education": clamp_score(education_score),
        "certifications": clamp_score(certification_score),
    }

    final_score = sum(
        component_scores[component] * weights[component]
        for component in component_scores
    )

    return round(clamp_score(final_score), 2)