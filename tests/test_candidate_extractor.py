"""Tests for the candidate information extraction module."""

from modules.candidate_extractor import (
    NOT_DETECTED,
    extract_candidate_information,
    extract_email,
    extract_name,
    extract_phone,
    calculate_experience_score,
    extract_experience,
    calculate_education_score,
    extract_education,
    load_education_keywords,
    calculate_certification_score,
    extract_certifications,
    load_certification_keywords,
    extract_all_certifications,
    extract_certification_section_entries,
)


def test_extract_email():
    """A valid email address must be extracted."""

    result = extract_email("Email: candidate.name@example.com")

    assert result == "candidate.name@example.com"


def test_missing_email():
    """Missing email must return the fallback value."""

    result = extract_email("No email address is provided.")

    assert result == NOT_DETECTED


def test_extract_phone_with_country_code():
    """An Indian mobile number with +91 must be extracted."""

    result = extract_phone("Phone: +91 98765 43210")

    assert result == "+91 98765 43210"


def test_extract_phone_with_hyphen():
    """An Indian mobile number with a hyphen must be extracted."""

    result = extract_phone("Contact: 98765-43210")

    assert result == "98765-43210"


def test_missing_phone():
    """Missing phone number must return the fallback value."""

    result = extract_phone("No phone number is provided.")

    assert result == NOT_DETECTED


def test_extract_name():
    """A likely candidate name must be extracted."""

    text = """RESUME
John Doe
Python Developer
john@example.com
"""

    result = extract_name(text)

    assert result == "John Doe"


def test_missing_name():
    """Missing candidate name must return the fallback value."""

    result = extract_name("")

    assert result == NOT_DETECTED


def test_extract_all_candidate_information():
    """All available basic candidate details must be returned."""

    text = """Jane Doe
Data Analyst
Email: jane.doe@example.com
Phone: +91 98765-43210
"""

    result = extract_candidate_information(text)

    assert result["name"] == "Jane Doe"
    assert result["email"] == "jane.doe@example.com"
    assert result["phone"] == "+91 98765-43210"


def test_empty_text_fallbacks():
    """Empty text must return fallback values for all fields."""

    result = extract_candidate_information("")

    assert result == {
        "name": NOT_DETECTED,
        "email": NOT_DETECTED,
        "phone": NOT_DETECTED,
        "experience": None,
    }

def test_extract_experience():
    """Explicit years of experience must be detected."""

    result = extract_experience(
        "Python developer with 3 years of experience."
    )

    assert result == 3.0


def test_extract_decimal_experience():
    """Decimal experience values must be detected."""

    result = extract_experience(
        "Data analyst with 2.5 years experience."
    )

    assert result == 2.5


def test_missing_experience():
    """Missing experience must remain undetected."""

    result = extract_experience(
        "Skilled in Python, SQL and Power BI."
    )

    assert result is None


def test_experience_meets_requirement():
    """A candidate meeting the requirement must score 100."""

    result = calculate_experience_score(3, 3)

    assert result == 100.0


def test_experience_exceeds_requirement():
    """A candidate exceeding the requirement must score 100."""

    result = calculate_experience_score(3, 5)

    assert result == 100.0


def test_experience_below_requirement():
    """Partial experience must receive a proportional score."""

    result = calculate_experience_score(4, 2)

    assert result == 50.0


def test_zero_required_experience():
    """A zero experience requirement must score 100."""

    result = calculate_experience_score(0, None)

    assert result == 100.0


def test_undetected_candidate_experience():
    """Undetected candidate experience must score zero."""

    result = calculate_experience_score(3, None)

    assert result == 0.0


def test_negative_experience():
    """Negative experience values must be rejected safely."""

    result = calculate_experience_score(3, -1)

    assert result == 0.0


def test_invalid_experience():
    """Invalid experience values must be handled safely."""

    result = calculate_experience_score("invalid", 3)

    assert result == 0.0

def test_load_education_keywords():
    """The education keyword database must load successfully."""

    education_keywords = load_education_keywords()

    assert "MBA" in education_keywords
    assert "B.Tech" in education_keywords
    assert "MCA" in education_keywords


def test_extract_single_education():
    """A single qualification must be detected."""

    education_keywords = load_education_keywords()

    result = extract_education(
        "Completed Master of Business Administration in 2025.",
        education_keywords,
    )

    assert "MBA" in result


def test_extract_multiple_education():
    """Multiple qualifications must be detected."""

    education_keywords = load_education_keywords()

    result = extract_education(
        "Completed BCA followed by MCA.",
        education_keywords,
    )

    assert "BCA" in result
    assert "MCA" in result


def test_education_case_insensitive():
    """Education detection must ignore letter case."""

    education_keywords = load_education_keywords()

    result = extract_education(
        "Candidate has completed mba.",
        education_keywords,
    )

    assert "MBA" in result


def test_missing_education():
    """Text without a known qualification must return an empty list."""

    education_keywords = load_education_keywords()

    result = extract_education(
        "Experienced Python developer.",
        education_keywords,
    )

    assert result == []


def test_exact_education_match():
    """An exact education match must score 100."""

    result = calculate_education_score(
        "MBA",
        ["B.Com", "MBA"],
    )

    assert result == 100.0


def test_unmatched_education():
    """An unmatched qualification must score zero."""

    result = calculate_education_score(
        "MBA",
        ["B.Tech"],
    )

    assert result == 0.0


def test_no_education_requirement():
    """No education requirement must not reduce the score."""

    result = calculate_education_score(
        "",
        [],
    )

    assert result == 100.0


def test_missing_candidate_education():
    """Missing candidate education must score zero when required."""

    result = calculate_education_score(
        "MBA",
        [],
    )

    assert result == 0.0
    
def test_load_certification_keywords():
    """The certification keyword database must load successfully."""

    certification_keywords = load_certification_keywords()

    assert "PMP" in certification_keywords
    assert "CAPM" in certification_keywords
    assert "PL-300" in certification_keywords


def test_extract_single_certification():
    """A single certification must be detected."""

    certification_keywords = load_certification_keywords()

    result = extract_certifications(
        "Certified Project Management Professional.",
        certification_keywords,
    )

    assert "PMP" in result


def test_extract_multiple_certifications():
    """Multiple certifications must be detected."""

    certification_keywords = load_certification_keywords()

    result = extract_certifications(
        "Certified in CAPM and PL-300.",
        certification_keywords,
    )

    assert "CAPM" in result
    assert "PL-300" in result


def test_certification_case_insensitive():
    """Certification detection must ignore letter case."""

    certification_keywords = load_certification_keywords()

    result = extract_certifications(
        "Candidate has completed pmp certification.",
        certification_keywords,
    )

    assert "PMP" in result


def test_missing_certification():
    """Text without a known certification must return an empty list."""

    certification_keywords = load_certification_keywords()

    result = extract_certifications(
        "Experienced Python developer.",
        certification_keywords,
    )

    assert result == []


def test_full_certification_match():
    """Matching all preferred certifications must score 100."""

    result = calculate_certification_score(
        ["PMP", "CAPM"],
        ["PMP", "CAPM", "PL-300"],
    )

    assert result == 100.0


def test_partial_certification_match():
    """Matching some preferred certifications must score proportionally."""

    result = calculate_certification_score(
        ["PMP", "CAPM"],
        ["PMP"],
    )

    assert result == 50.0


def test_no_certification_match():
    """Matching no preferred certifications must score zero."""

    result = calculate_certification_score(
        ["PMP"],
        ["PL-300"],
    )

    assert result == 0.0


def test_no_certification_requirement():
    """No preferred certifications must not reduce the score."""

    result = calculate_certification_score(
        [],
        [],
    )

    assert result == 100.0
    
def test_extract_dynamic_certification_section():
    """Unknown certifications must be extracted from the section."""

    text = """
John Doe

CERTIFICATIONS
Google Project Management Professional Certificate
IBM Data Analyst Professional Certificate

EDUCATION
MBA
"""

    result = extract_certification_section_entries(text)

    assert result == [
        "Google Project Management Professional Certificate",
        "IBM Data Analyst Professional Certificate",
    ]


def test_extract_dynamic_certifications_with_bullets():
    """Certification bullet markers must be removed."""

    text = """
CERTIFICATIONS
- Python for Everybody
• Google Data Analytics Professional Certificate

SKILLS
Python
"""

    result = extract_certification_section_entries(text)

    assert result == [
        "Python for Everybody",
        "Google Data Analytics Professional Certificate",
    ]


def test_extract_all_certifications_combines_sources():
    """Known and unknown certifications must be combined."""

    certification_keywords = {
        "PMP": [
            "PMP",
            "Project Management Professional",
        ]
    }

    text = """
CERTIFICATIONS
PMP
IBM Data Analyst Professional Certificate

EDUCATION
MBA
"""

    result = extract_all_certifications(
        text,
        certification_keywords,
    )

    assert "PMP" in result
    assert "IBM Data Analyst Professional Certificate" in result
    assert result.count("PMP") == 1

def test_ignore_empty_certification_separator_lines():
    """Separator-only lines must not become certifications."""

    text = """
CERTIFICATIONS
,
|
-
Microsoft Excel: Beginner to Advanced

EDUCATION
MBA
"""

    result = extract_certification_section_entries(text)

    assert result == [
        "Microsoft Excel: Beginner to Advanced",
    ]