"""Tests for complete system orchestration."""

from io import BytesIO

import fitz
from docx import Document

from modules.orchestrator import (
    get_saved_rankings,
    process_resume_batch,
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


def test_complete_batch_workflow(tmp_path):
    """Valid resumes must be screened, saved, and ranked."""

    database_path = tmp_path / "test.db"

    resumes = [
        (
            "candidate_one.pdf",
            create_test_pdf(
                "John Doe\n"
                "3 years of experience\n"
                "MBA\n"
                "PMP\n"
                "Python SQL Power BI"
            ),
        ),
        (
            "candidate_two.docx",
            create_test_docx(
                "Jane Doe\n"
                "2 years of experience\n"
                "BCA\n"
                "Python"
            ),
        ),
    ]

    result = process_resume_batch(
        resumes=resumes,
        job_description="Python SQL Power BI developer",
        required_experience=3,
        required_education="MBA",
        required_certifications=["PMP"],
        database_path=str(database_path),
    )

    assert len(result["ranked_candidates"]) == 2
    assert result["failed_resumes"] == []
    assert result["ranked_candidates"][0]["rank"] == 1
    assert result["ranked_candidates"][1]["rank"] == 2


def test_corrupted_resume_isolated(tmp_path):
    """A corrupted resume must not stop valid candidates."""

    database_path = tmp_path / "test.db"

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

    result = process_resume_batch(
        resumes=resumes,
        job_description="Python developer",
        database_path=str(database_path),
    )

    assert len(result["ranked_candidates"]) == 1
    assert len(result["failed_resumes"]) == 1
    assert result["failed_resumes"][0]["file_name"] == "corrupted.pdf"


def test_same_resume_can_be_processed_again(tmp_path):
    """The same resume must be allowed to be screened repeatedly."""

    database_path = tmp_path / "test.db"

    resume_content = create_test_pdf(
        "John Doe\nPython SQL"
    )

    first_result = process_resume_batch(
        resumes=[("resume.pdf", resume_content)],
        job_description="Python developer",
        database_path=str(database_path),
    )

    second_result = process_resume_batch(
        resumes=[("resume.pdf", resume_content)],
        job_description="Python developer",
        database_path=str(database_path),
    )

    assert len(first_result["ranked_candidates"]) == 1
    assert first_result["failed_resumes"] == []

    assert len(second_result["ranked_candidates"]) == 1
    assert second_result["failed_resumes"] == []

    saved_rankings = get_saved_rankings(
        str(database_path)
    )

    assert len(saved_rankings) == 2


def test_get_saved_rankings(tmp_path):
    """Stored candidates must be returned with rank numbers."""

    database_path = tmp_path / "test.db"

    process_resume_batch(
        resumes=[
            (
                "candidate.pdf",
                create_test_pdf("John Doe\nPython SQL"),
            )
        ],
        job_description="Python developer",
        database_path=str(database_path),
    )

    rankings = get_saved_rankings(str(database_path))

    assert len(rankings) == 1
    assert rankings[0]["rank"] == 1


def test_empty_batch(tmp_path):
    """An empty batch must return empty result lists."""

    database_path = tmp_path / "test.db"

    result = process_resume_batch(
        resumes=[],
        job_description="Python developer",
        database_path=str(database_path),
    )

    assert result == {
        "ranked_candidates": [],
        "failed_resumes": [],
    }