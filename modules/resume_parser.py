"""Extract text from PDF and DOCX resume files."""

from io import BytesIO
from pathlib import Path

import fitz
from docx import Document


def extract_text_from_pdf(file_content: bytes) -> tuple[str, bool, str]:
    """Extract text from a PDF file without crashing the application."""

    if not file_content:
        return "", False, "The PDF file is empty."

    try:
        document = fitz.open(stream=file_content, filetype="pdf")

        if document.needs_pass:
            document.close()
            return "", False, "The PDF is password-protected."

        extracted_text = ""

        for page in document:
            extracted_text += page.get_text() + "\n"

        document.close()
        cleaned_text = extracted_text.strip()

        if not cleaned_text:
            return "", False, "No readable text was found in the PDF."

        return cleaned_text, True, ""

    except Exception as error:
        return "", False, f"The PDF could not be processed: {error}"


def extract_text_from_docx(file_content: bytes) -> tuple[str, bool, str]:
    """Extract text from a DOCX file without crashing the application."""

    if not file_content:
        return "", False, "The DOCX file is empty."

    try:
        document = Document(BytesIO(file_content))

        extracted_text = "\n".join(
            paragraph.text for paragraph in document.paragraphs
        ).strip()

        if not extracted_text:
            return "", False, "No readable text was found in the DOCX file."

        return extracted_text, True, ""

    except Exception as error:
        return "", False, f"The DOCX file could not be processed: {error}"


def extract_resume_text(
    file_name: str,
    file_content: bytes,
) -> tuple[str, bool, str]:
    """Select the correct parser based on the resume file extension."""

    file_extension = Path(file_name).suffix.lower()

    if file_extension == ".pdf":
        return extract_text_from_pdf(file_content)

    if file_extension == ".docx":
        return extract_text_from_docx(file_content)

    return "", False, "Unsupported file format."