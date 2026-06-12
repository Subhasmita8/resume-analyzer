"""
parser.py
---------
Handles text extraction from uploaded resume files.
Supports PDF (via PyPDF2) and DOCX (via python-docx).
"""

import io
import PyPDF2
import docx


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract all text from a PDF file given its raw bytes.

    Args:
        file_bytes: Raw bytes of the PDF file.

    Returns:
        Extracted text as a single string.

    Raises:
        ValueError: If the PDF cannot be read or has no extractable text.
    """
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))

        if len(reader.pages) == 0:
            raise ValueError("PDF has no pages.")

        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        full_text = "\n".join(text_parts).strip()

        if not full_text:
            raise ValueError("No extractable text found in PDF. It may be image-based.")

        return full_text

    except PyPDF2.errors.PdfReadError as e:
        raise ValueError(f"Invalid or corrupted PDF file: {e}")


def extract_text_from_docx(file_bytes: bytes) -> str:
    """
    Extract all text from a DOCX file given its raw bytes.

    Args:
        file_bytes: Raw bytes of the DOCX file.

    Returns:
        Extracted text as a single string.

    Raises:
        ValueError: If the DOCX cannot be read or has no extractable text.
    """
    try:
        doc = docx.Document(io.BytesIO(file_bytes))

        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        full_text = "\n".join(paragraphs).strip()

        if not full_text:
            raise ValueError("No text found in DOCX file.")

        return full_text

    except Exception as e:
        raise ValueError(f"Could not read DOCX file: {e}")


def parse_resume(file_bytes: bytes, filename: str) -> str:
    """
    Route parsing based on file extension.

    Args:
        file_bytes: Raw bytes of the uploaded file.
        filename: Original filename (used to detect type).

    Returns:
        Extracted plain text from the resume.

    Raises:
        ValueError: If the file type is unsupported.
    """
    lower_name = filename.lower()

    if lower_name.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif lower_name.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    else:
        raise ValueError(
            f"Unsupported file type: '{filename}'. Please upload a PDF or DOCX file."
        )
