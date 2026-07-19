"""Tests for the complete resume screening pipeline."""

from io import BytesIO

import fitz
import pytest
from docx import Document

from modules.screening_pipeline import screen_resume

from modules.screening_pipeline import (
    screen_multiple_resumes,
    screen_resume,
)


def create_test_pdf(text: str) -> bytes:
    """Create a valid PDF containing test resume text."""

    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    pdf_content = document.tobytes()
    document.close()

    return pdf_content


def create_test_docx(text: str) -> bytes:
    """Create a valid DOCX containing test resume text."""

    document = Document()
    document.add_paragraph(text)

    file_stream = BytesIO()
    document.save(file_stream)

    return file_stream.getvalue()


def test_complete_pdf_pipeline():
    """A valid PDF must pass through the complete pipeline."""

    resume_text = """
John Doe
john@example.com
+91 98765 43210
3 years of experience
MBA
PMP
Python SQL Power BI
"""

    result = screen_resume(
        file_name="john_resume.pdf",
        file_content=create_test_pdf(resume_text),
        job_description="Python SQL Power BI developer",
        required_experience=3,
        required_education="MBA",
        required_certifications=["PMP"],
    )

    assert result["file_name"] == "john_resume.pdf"
    assert result["name"] == "John Doe"
    assert result["email"] == "john@example.com"
    assert result["experience"] == 3.0
    assert "MBA" in result["education"]
    assert "PMP" in result["certifications"]
    assert "Python" in result["skills"]
    assert 0.0 <= result["final_score"] <= 100.0


def test_complete_docx_pipeline():
    """A valid DOCX must pass through the complete pipeline."""

    resume_text = """
Jane Doe
jane@example.com
2 years of experience
BCA
Python SQL
"""

    result = screen_resume(
        file_name="jane_resume.docx",
        file_content=create_test_docx(resume_text),
        job_description="Python SQL developer",
        required_experience=2,
        required_education="BCA",
    )

    assert result["name"] == "Jane Doe"
    assert result["email"] == "jane@example.com"
    assert result["experience"] == 2.0
    assert "BCA" in result["education"]
    assert result["final_score"] > 0.0


def test_empty_job_description():
    """An empty job description must be rejected."""

    with pytest.raises(
        ValueError,
        match="The job description cannot be empty.",
    ):
        screen_resume(
            file_name="resume.pdf",
            file_content=create_test_pdf("John Doe"),
            job_description="",
        )


def test_corrupted_resume():
    """A corrupted resume must fail safely."""

    with pytest.raises(ValueError):
        screen_resume(
            file_name="corrupted.pdf",
            file_content=b"Not a real PDF",
            job_description="Python developer",
        )


def test_pipeline_result_contains_required_fields():
    """The result must contain all fields required by the database."""

    result = screen_resume(
        file_name="resume.pdf",
        file_content=create_test_pdf(
            "John Doe\nPython developer"
        ),
        job_description="Python developer",
    )

    required_fields = {
        "file_name",
        "file_hash",
        "name",
        "email",
        "phone",
        "experience",
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

    assert required_fields.issubset(result.keys())

def test_multiple_resume_processing():
    """Multiple valid resumes must be processed successfully."""

    resumes = [
        (
            "candidate_one.pdf",
            create_test_pdf(
                "John Doe\n"
                "3 years of experience\n"
                "Python SQL"
            ),
        ),
        (
            "candidate_two.docx",
            create_test_docx(
                "Jane Doe\n"
                "2 years of experience\n"
                "Python Power BI"
            ),
        ),
    ]

    result = screen_multiple_resumes(
        resumes=resumes,
        job_description="Python SQL Power BI developer",
    )

    assert len(result["successful_candidates"]) == 2
    assert result["failed_resumes"] == []


def test_failed_resume_does_not_stop_processing():
    """One corrupted resume must not stop valid resumes."""

    resumes = [
        (
            "valid.pdf",
            create_test_pdf("John Doe\nPython SQL"),
        ),
        (
            "corrupted.pdf",
            b"Not a real PDF",
        ),
    ]

    result = screen_multiple_resumes(
        resumes=resumes,
        job_description="Python developer",
    )

    assert len(result["successful_candidates"]) == 1
    assert len(result["failed_resumes"]) == 1
    assert result["failed_resumes"][0]["file_name"] == "corrupted.pdf"


def test_empty_resume_list():
    """An empty resume list must return empty result lists."""

    result = screen_multiple_resumes(
        resumes=[],
        job_description="Python developer",
    )

    assert result == {
        "successful_candidates": [],
        "failed_resumes": [],
    }


def test_all_resumes_fail():
    """Multiple failed resumes must all be reported."""

    resumes = [
        ("corrupted_one.pdf", b"Invalid PDF"),
        ("corrupted_two.docx", b"Invalid DOCX"),
    ]

    result = screen_multiple_resumes(
        resumes=resumes,
        job_description="Python developer",
    )

    assert result["successful_candidates"] == []
    assert len(result["failed_resumes"]) == 2