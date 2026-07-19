"""Preprocess resume and job description text for different tasks."""

import re
import unicodedata


def normalize_whitespace(text: str) -> str:
    """Normalize repeated spaces and blank lines."""

    if not text:
        return ""

    return re.sub(r"\s+", " ", text).strip()


def prepare_for_candidate_extraction(text: str) -> str:
    """Clean text while preserving contact details and original casing."""

    if not text:
        return ""

    normalized_text = unicodedata.normalize("NFKC", text)

    return normalize_whitespace(normalized_text)


def prepare_for_similarity(text: str) -> str:
    """Prepare text for NLP similarity analysis."""

    if not text:
        return ""

    normalized_text = unicodedata.normalize("NFKC", text)
    normalized_text = normalized_text.lower()

    # Preserve important technical terms before removing punctuation.
    replacements = {
        "c++": "cplusplus",
        "c#": "csharp",
        ".net": "dotnet",
        "power bi": "powerbi",
    }

    for original_term, protected_term in replacements.items():
        normalized_text = normalized_text.replace(
            original_term,
            protected_term,
        )

    normalized_text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        normalized_text,
    )

    return normalize_whitespace(normalized_text)