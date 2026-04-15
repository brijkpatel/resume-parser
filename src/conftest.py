"""Pytest configuration and fixtures for the entire project."""

from pathlib import Path
import pytest
from dotenv import load_dotenv

# Load environment variables from .env file
# This ensures tests have access to API keys and other config
load_dotenv()

# Get src directory path
src_path = Path(__file__).parent


@pytest.fixture(scope="session", autouse=True)
def setup_parser_test_data():
    """Generate all test fixture files for parser tests before the suite runs.

    PDF and DOCX generation are kept in separate try/except blocks so that a
    failure in one (e.g. a missing library) does not prevent the other from
    running.
    """
    data_dir = src_path / "parsers" / "tests" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    # --- PDF fixtures -------------------------------------------------------
    try:
        from parsers.tests.generate_test_pdfs import (
            create_simple_pdf,
            create_pdf_with_tables,
            create_multipage_pdf,
            create_pdf_with_special_chars,
            create_images_only_pdf,
            create_password_protected_pdf,
            create_large_pdf,
        )

        create_simple_pdf()
        create_pdf_with_tables()
        create_multipage_pdf()
        create_pdf_with_special_chars()
        create_images_only_pdf()
        create_password_protected_pdf()
        create_large_pdf()

        # Stub edge-case PDF files
        (data_dir / "empty.pdf").write_bytes(b"")
        (data_dir / "corrupted.pdf").write_text("corrupted content")
        (data_dir / "fake.pdf").write_text("This is not a PDF file")

    except Exception as e:
        print(f"Warning: Failed to generate PDF test data: {e}")

    # --- DOCX / DOC fixtures ------------------------------------------------
    try:
        from parsers.tests.generate_test_data import (
            create_simple_docx,
            create_docx_with_tables,
            create_empty_content_docx,
            create_formatted_docx,
            create_images_only_docx,
            create_special_chars_docx,
            create_headers_docx,
            create_lists_docx,
            create_large_docx,
            create_empty_paragraphs_docx,
            create_nested_tables_docx,
            create_legacy_doc,
        )

        create_simple_docx()
        create_docx_with_tables()
        create_empty_content_docx()
        create_formatted_docx()
        create_images_only_docx()
        create_special_chars_docx()
        create_headers_docx()
        create_lists_docx()
        create_large_docx()
        create_empty_paragraphs_docx()
        create_nested_tables_docx()
        create_legacy_doc()

        # Stub edge-case DOCX/misc files
        (data_dir / "empty.docx").write_bytes(b"")
        (data_dir / "corrupted.docx").write_text("corrupted content")
        (data_dir / "fake.docx").write_text("This is not a DOCX file")
        (data_dir / "sample.txt").write_text(
            "This is a plain text file.\nIt should not be parsed as a PDF or DOCX."
        )

    except Exception as e:
        print(f"Warning: Failed to generate DOCX test data: {e}")

    yield
