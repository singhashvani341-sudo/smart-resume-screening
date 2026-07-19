"""Tests for the file validation module."""

from modules.file_validator import validate_file
from io import BytesIO

import fitz
from docx import Document


def test_empty_file():
    """An empty file must be rejected."""

    uploaded_hashes = set()

    is_valid, message = validate_file(
        file_name="empty.pdf",
        file_content=b"",
        uploaded_hashes=uploaded_hashes,
    )

    assert is_valid is False
    assert message == "The uploaded file is empty."


def test_unsupported_file_format():
    """An unsupported file type must be rejected."""

    uploaded_hashes = set()

    is_valid, message = validate_file(
        file_name="resume.txt",
        file_content=b"Sample resume content",
        uploaded_hashes=uploaded_hashes,
    )

    assert is_valid is False
    assert message == "Unsupported file format."


def test_missing_file_name():
    """A missing file name must be rejected."""

    uploaded_hashes = set()

    is_valid, message = validate_file(
        file_name="",
        file_content=b"Sample content",
        uploaded_hashes=uploaded_hashes,
    )

    assert is_valid is False
    assert message == "The file name is missing."


def test_oversized_file():
    """A file larger than the configured limit must be rejected."""

    uploaded_hashes = set()
    oversized_content = b"a" * (10 * 1024 * 1024 + 1)

    is_valid, message = validate_file(
        file_name="large.pdf",
        file_content=oversized_content,
        uploaded_hashes=uploaded_hashes,
    )

    assert is_valid is False
    assert message == "The file exceeds the maximum size limit."


def test_corrupted_pdf():
    """A corrupted PDF must be rejected."""

    uploaded_hashes = set()

    is_valid, message = validate_file(
        file_name="corrupted.pdf",
        file_content=b"This is not a real PDF file.",
        uploaded_hashes=uploaded_hashes,
    )

    assert is_valid is False
    assert message == "The PDF could not be read."


def test_corrupted_docx():
    """A corrupted DOCX file must be rejected."""

    uploaded_hashes = set()

    is_valid, message = validate_file(
        file_name="corrupted.docx",
        file_content=b"This is not a real DOCX file.",
        uploaded_hashes=uploaded_hashes,
    )

    assert is_valid is False
    assert message == "The DOCX file could not be read."
    
def test_valid_pdf():
    """A valid PDF must be accepted."""

    document = fitz.open()
    document.new_page()
    pdf_content = document.tobytes()
    document.close()

    uploaded_hashes = set()

    is_valid, message = validate_file(
        file_name="resume.pdf",
        file_content=pdf_content,
        uploaded_hashes=uploaded_hashes,
    )

    assert is_valid is True
    assert message == "File is valid."


def test_valid_docx():
    """A valid DOCX file must be accepted."""

    document = Document()
    document.add_paragraph("Sample resume content")

    file_stream = BytesIO()
    document.save(file_stream)

    uploaded_hashes = set()

    is_valid, message = validate_file(
        file_name="resume.docx",
        file_content=file_stream.getvalue(),
        uploaded_hashes=uploaded_hashes,
    )

    assert is_valid is True
    assert message == "File is valid."


def test_duplicate_file():
    """The same file content must not be accepted twice."""

    document = fitz.open()
    document.new_page()
    pdf_content = document.tobytes()
    document.close()

    uploaded_hashes = set()

    first_result, _ = validate_file(
        file_name="resume.pdf",
        file_content=pdf_content,
        uploaded_hashes=uploaded_hashes,
    )

    second_result, message = validate_file(
        file_name="resume_copy.pdf",
        file_content=pdf_content,
        uploaded_hashes=uploaded_hashes,
    )

    assert first_result is True
    assert second_result is False
    assert message == "This file has already been uploaded."