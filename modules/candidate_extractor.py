"""Extract candidate information from resume text."""

import re
from typing import Optional
from pathlib import Path

import pandas as pd


NOT_DETECTED = "Not detected"

DEFAULT_EDUCATION_FILE = Path("data/education_keywords.csv")
DEFAULT_CERTIFICATION_FILE = Path("data/certification_keywords.csv")

def extract_email(text: str) -> str:
    """Extract the first valid email address from resume text."""

    if not text:
        return NOT_DETECTED

    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    match = re.search(email_pattern, text)

    return match.group(0) if match else NOT_DETECTED


def extract_phone(text: str) -> str:
    """Extract the first common Indian mobile number from resume text."""

    if not text:
        return NOT_DETECTED

    phone_pattern = r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}(?!\d)"
    match = re.search(phone_pattern, text)

    return match.group(0).strip() if match else NOT_DETECTED


def extract_name(text: str) -> str:
    """Estimate the candidate name using the first suitable resume line."""

    if not text:
        return NOT_DETECTED

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    ignored_terms = {
        "resume",
        "curriculum vitae",
        "cv",
        "profile",
        "professional summary",
    }

    for line in lines[:5]:
        cleaned_line = re.sub(r"[^A-Za-z\s.'-]", "", line).strip()
        words = cleaned_line.split()

        if (
            2 <= len(words) <= 4
            and cleaned_line.lower() not in ignored_terms
            and all(len(word) > 1 for word in words)
        ):
            return cleaned_line

    return NOT_DETECTED


def extract_experience(text: str) -> Optional[float]:
    """Estimate years of experience from explicit resume statements."""

    if not text:
        return None

    experience_patterns = [
        r"(\d+(?:\.\d+)?)\+?\s*years?\s+of\s+experience",
        r"experience\s+of\s+(\d+(?:\.\d+)?)\+?\s*years?",
        r"(\d+(?:\.\d+)?)\+?\s*years?\s+experience",
    ]

    detected_values = []

    for pattern in experience_patterns:
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        detected_values.extend(float(value) for value in matches)

    if not detected_values:
        return None

    return max(detected_values)


def calculate_experience_score(
    required_experience: float,
    candidate_experience: Optional[float],
) -> float:
    """Calculate experience match score on a 0 to 100 scale."""

    try:
        required_experience = float(required_experience)
    except (TypeError, ValueError):
        return 0.0

    if required_experience < 0:
        return 0.0

    if required_experience == 0:
        return 100.0

    if candidate_experience is None:
        return 0.0

    try:
        candidate_experience = float(candidate_experience)
    except (TypeError, ValueError):
        return 0.0

    if candidate_experience < 0:
        return 0.0

    if candidate_experience >= required_experience:
        return 100.0

    score = (
        candidate_experience
        / required_experience
        * 100
    )

    return round(max(0.0, min(100.0, score)), 2)


def load_education_keywords(
    file_path: Path = DEFAULT_EDUCATION_FILE,
) -> dict[str, list[str]]:
    """Load education qualifications and their keyword variants."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"Education keyword database not found: {file_path}"
        )

    education_dataframe = pd.read_csv(file_path)

    required_columns = {"education", "keyword"}

    if not required_columns.issubset(education_dataframe.columns):
        raise ValueError(
            "The education database must contain "
            "'education' and 'keyword' columns."
        )

    education_keywords = {}

    for _, row in education_dataframe.iterrows():
        education = str(row["education"]).strip()
        keyword = str(row["keyword"]).strip()

        if education and keyword:
            education_keywords.setdefault(
                education,
                [],
            ).append(keyword)

    return education_keywords


def extract_education(
    text: str,
    education_keywords: dict[str, list[str]],
) -> list[str]:
    """Detect known education qualifications in resume text."""

    if not text or not education_keywords:
        return []

    detected_education = []

    for education, keywords in education_keywords.items():
        for keyword in keywords:
            pattern = rf"(?<!\w){re.escape(keyword)}(?!\w)"

            if re.search(pattern, text, flags=re.IGNORECASE):
                detected_education.append(education)
                break

    return detected_education


def calculate_education_score(
    required_education: str,
    candidate_education: list[str],
) -> float:
    """Calculate education match score using transparent exact matching."""

    if not required_education or not required_education.strip():
        return 100.0

    if not candidate_education:
        return 0.0

    normalized_requirement = required_education.strip().lower()

    normalized_candidate_education = {
        education.strip().lower()
        for education in candidate_education
    }

    if normalized_requirement in normalized_candidate_education:
        return 100.0

    return 0.0

def load_certification_keywords(
    file_path: Path = DEFAULT_CERTIFICATION_FILE,
) -> dict[str, list[str]]:
    """Load certifications and their keyword variants."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"Certification keyword database not found: {file_path}"
        )

    certification_dataframe = pd.read_csv(file_path)

    required_columns = {"certification", "keyword"}

    if not required_columns.issubset(certification_dataframe.columns):
        raise ValueError(
            "The certification database must contain "
            "'certification' and 'keyword' columns."
        )

    certification_keywords = {}

    for _, row in certification_dataframe.iterrows():
        certification = str(row["certification"]).strip()
        keyword = str(row["keyword"]).strip()

        if certification and keyword:
            certification_keywords.setdefault(
                certification,
                [],
            ).append(keyword)

    return certification_keywords


def extract_certifications(
    text: str,
    certification_keywords: dict[str, list[str]],
) -> list[str]:
    """Detect known certifications in resume text."""

    if not text or not certification_keywords:
        return []

    detected_certifications = []

    for certification, keywords in certification_keywords.items():
        for keyword in keywords:
            pattern = rf"(?<!\w){re.escape(keyword)}(?!\w)"

            if re.search(pattern, text, flags=re.IGNORECASE):
                detected_certifications.append(certification)
                break

    return detected_certifications
def extract_certification_section_entries(
    text: str,
) -> list[str]:
    """Extract certification names directly from resume sections."""

    if not text:
        return []

    section_headings = {
        "certification",
        "certifications",
        "certificate",
        "certificates",
        "licenses and certifications",
        "licenses & certifications",
        "professional certifications",
    }

    stop_headings = {
        "education",
        "experience",
        "work experience",
        "professional experience",
        "skills",
        "technical skills",
        "projects",
        "achievements",
        "awards",
        "languages",
        "interests",
        "summary",
        "profile",
    }

    lines = [
        line.strip()
        for line in text.splitlines()
    ]

    certification_entries = []
    inside_certification_section = False

    for line in lines:
        cleaned_line = line.strip(" :-").strip()
        normalized_line = cleaned_line.lower()

        if normalized_line in section_headings:
            inside_certification_section = True
            continue

        if (
            inside_certification_section
            and normalized_line in stop_headings
        ):
            break

        if not inside_certification_section:
            continue

        if not cleaned_line:
            continue

        cleaned_entry = re.sub(
            r"^[•●▪■\-–—*|]+\s*",
            "",
            cleaned_line,
        ).strip()

        if (
            cleaned_entry
            and re.search(r"[A-Za-z0-9]", cleaned_entry)
        ):
            certification_entries.append(cleaned_entry)
            
    return certification_entries

def extract_all_certifications(
    text: str,
    certification_keywords: dict[str, list[str]],
) -> list[str]:
    """Combine known and dynamically extracted certifications."""

    known_certifications = extract_certifications(
        text,
        certification_keywords,
    )

    dynamic_certifications = extract_certification_section_entries(
        text
    )

    combined_certifications = []
    seen_certifications = set()

    for certification in (
        known_certifications + dynamic_certifications
    ):
        normalized_certification = certification.strip().lower()

        if (
            normalized_certification
            and normalized_certification not in seen_certifications
        ):
            combined_certifications.append(
                certification.strip()
            )
            seen_certifications.add(
                normalized_certification
            )

    return combined_certifications


def calculate_certification_score(
    required_certifications: list[str],
    candidate_certifications: list[str],
) -> float:
    """Calculate certification match score on a 0 to 100 scale."""

    if not required_certifications:
        return 100.0

    required_lookup = {
        certification.strip().lower()
        for certification in required_certifications
        if certification.strip()
    }

    if not required_lookup:
        return 100.0

    candidate_lookup = {
        certification.strip().lower()
        for certification in candidate_certifications
        if certification.strip()
    }

    matched_certifications = required_lookup & candidate_lookup

    score = (
        len(matched_certifications)
        / len(required_lookup)
        * 100
    )

    return round(max(0.0, min(100.0, score)), 2)

def extract_candidate_information(text: str) -> dict[str, object]:
    """Extract candidate details with safe fallback values."""

    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "experience": extract_experience(text),
    }