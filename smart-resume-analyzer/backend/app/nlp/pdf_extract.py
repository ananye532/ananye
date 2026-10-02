"""PDF to plain text using pdfplumber."""

from __future__ import annotations

import io
from dataclasses import dataclass

import pdfplumber
from pdfminer.pdfdocument import PDFPasswordIncorrect
from pdfplumber.utils.exceptions import PdfminerException

from .preprocessing import clean_text

PDF_MAGIC = b"%PDF-"
MIN_TEXT_CHARS = 50


class PDFExtractionError(ValueError):
    """Raised for any PDF the extractor will not or cannot process. `code` is stable for clients."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class ExtractedPDF:
    text: str
    page_count: int


def extract_text_from_pdf(data: bytes, max_pages: int = 10) -> ExtractedPDF:
    if not data.startswith(PDF_MAGIC):
        raise PDFExtractionError("not_pdf", "File content is not a PDF.")
    try:
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            page_count = len(pdf.pages)
            if page_count == 0:
                raise PDFExtractionError("empty_pdf", "The PDF has no pages.")
            if page_count > max_pages:
                raise PDFExtractionError(
                    "too_many_pages", f"The PDF has {page_count} pages; the limit is {max_pages}."
                )
            pages = [page.extract_text() or "" for page in pdf.pages]
    except PDFExtractionError:
        raise
    except PDFPasswordIncorrect as exc:  # raised unwrapped by some pdfplumber/pdfminer versions
        raise PDFExtractionError("encrypted_pdf", "Password-protected PDFs are not supported.") from exc
    except PdfminerException as exc:
        if exc.args and isinstance(exc.args[0], PDFPasswordIncorrect):
            raise PDFExtractionError("encrypted_pdf", "Password-protected PDFs are not supported.") from exc
        raise PDFExtractionError("corrupt_pdf", "The PDF could not be parsed.") from exc
    except Exception as exc:  # pdfminer raises many unrelated types on malformed input
        raise PDFExtractionError("corrupt_pdf", "The PDF could not be parsed.") from exc

    text = clean_text("\n".join(pages))
    if len(text) < MIN_TEXT_CHARS:
        raise PDFExtractionError(
            "no_text",
            "Almost no text could be extracted. The PDF may be a scanned image; OCR is not supported.",
        )
    return ExtractedPDF(text=text, page_count=page_count)
