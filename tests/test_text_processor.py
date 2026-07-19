"""Tests for the text preprocessing module."""

from modules.text_processor import (
    normalize_whitespace,
    prepare_for_candidate_extraction,
    prepare_for_similarity,
)


def test_normalize_whitespace():
    """Repeated whitespace must be normalized."""

    text = "Python    SQL\n\nPower BI"

    result = normalize_whitespace(text)

    assert result == "Python SQL Power BI"


def test_empty_input():
    """Empty input must return an empty string."""

    assert normalize_whitespace("") == ""
    assert prepare_for_candidate_extraction("") == ""
    assert prepare_for_similarity("") == ""


def test_candidate_extraction_preserves_email():
    """Email addresses must remain intact."""

    text = "Email: Candidate.Name@example.com"

    result = prepare_for_candidate_extraction(text)

    assert "Candidate.Name@example.com" in result


def test_candidate_extraction_preserves_phone():
    """Phone number formatting must remain intact."""

    text = "Phone: +91 98765-43210"

    result = prepare_for_candidate_extraction(text)

    assert "+91 98765-43210" in result


def test_similarity_converts_to_lowercase():
    """Similarity text must be converted to lowercase."""

    result = prepare_for_similarity("Python SQL EXCEL")

    assert result == "python sql excel"


def test_similarity_preserves_cpp():
    """C++ must be protected during preprocessing."""

    result = prepare_for_similarity("Experience with C++")

    assert "cplusplus" in result


def test_similarity_preserves_csharp():
    """C# must be protected during preprocessing."""

    result = prepare_for_similarity("Experience with C#")

    assert "csharp" in result


def test_similarity_preserves_dotnet():
    """.NET must be protected during preprocessing."""

    result = prepare_for_similarity("Experience with .NET")

    assert "dotnet" in result


def test_similarity_preserves_power_bi():
    """Power BI must be protected during preprocessing."""

    result = prepare_for_similarity("Experience with Power BI")

    assert "powerbi" in result


def test_unicode_normalization():
    """Unicode text must be handled safely."""

    result = prepare_for_candidate_extraction("José Kumar")

    assert result == "José Kumar"