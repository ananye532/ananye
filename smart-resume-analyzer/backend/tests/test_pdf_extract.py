import pytest

from app.nlp.pdf_extract import PDFExtractionError, extract_text_from_pdf

from .conftest import make_blank_pdf, make_pdf


def test_extracts_text_and_page_count():
    result = extract_text_from_pdf(make_pdf(pages=2))
    assert result.page_count == 2
    assert "Senior Software Engineer" in result.text
    assert "jane.doe@example.com" in result.text


def test_preserves_lines_for_section_detection():
    lines = extract_text_from_pdf(make_pdf()).text.split("\n")
    assert "Experience" in lines and "Education" in lines


@pytest.mark.parametrize(
    "data, code",
    [
        (b"PK\x03\x04 this is a zip", "not_pdf"),
        (b"%PDF-1.7\n garbage that is not a pdf", "corrupt_pdf"),
    ],
)
def test_rejects_invalid_content(data, code):
    with pytest.raises(PDFExtractionError) as e:
        extract_text_from_pdf(data)
    assert e.value.code == code


def test_rejects_too_many_pages():
    with pytest.raises(PDFExtractionError) as e:
        extract_text_from_pdf(make_pdf(pages=4), max_pages=3)
    assert e.value.code == "too_many_pages"


def test_rejects_image_only_pdf():
    with pytest.raises(PDFExtractionError) as e:
        extract_text_from_pdf(make_blank_pdf())
    assert e.value.code == "no_text"


def test_rejects_password_protected_pdf():
    with pytest.raises(PDFExtractionError) as e:
        extract_text_from_pdf(make_pdf(encrypt="s3cret"))
    assert e.value.code == "encrypted_pdf"
