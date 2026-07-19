"""Validate uploaded resume files before processing."""

from pathlib import Path
from typing import BinaryIO

import fitz
from docx import Document

from config import MAX_FILE_SIZE_BYTES, SUPPORTED_FILE_EXTENSIONS


def validate_file(
    file_name: str,
    file_content: bytes,
    uploaded_hashes: set[str],
) -> tuple[bool, str]:
    """Validate one uploaded resume file."""

    if not file_name:
        return False, "The file name is missing."

    if not file_content:
        return False, "The uploaded file is empty."

    file_extension = Path(file_name).suffix.lower()

    if file_extension not in SUPPORTED_FILE_EXTENSIONS:
        return False, "Unsupported file format."

    if len(file_content) > MAX_FILE_SIZE_BYTES:
        return False, "The file exceeds the maximum size limit."

    import hashlib

    file_hash = hashlib.sha256(file_content).hexdigest()

    if file_hash in uploaded_hashes:
        return False, "This file has already been uploaded."

    try:
        if file_extension == ".pdf":
            document = fitz.open(stream=file_content, filetype="pdf")
            document.close()

        elif file_extension == ".docx":
            from io import BytesIO

            Document(BytesIO(file_content))

    except Exception:
        if file_extension == ".pdf":
            return False, "The PDF could not be read."

        return False, "The DOCX file could not be read."

    uploaded_hashes.add(file_hash)

    return True, "File is valid."