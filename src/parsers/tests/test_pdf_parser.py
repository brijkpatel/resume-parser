"""Comprehensive tests for PDF parser."""

import pytest
from pathlib import Path
from parsers.pdf_parser import PDFParser
from exceptions import FileParsingError


# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "data"


class TestPDFParserInitialization:
    """Test PDF parser initialization."""

    def test_initialization(self):
        """Test that PDFParser initializes correctly."""
        parser = PDFParser()
        assert parser is not None
        assert parser.supported_extensions == [".pdf"]


class TestPDFParserValidFiles:
    """Test PDF parser with valid files."""

    @pytest.fixture
    def parser(self):
        """Create a PDFParser instance."""
        return PDFParser()

    def test_parse_valid_pdf(self, parser: PDFParser):
        """Test parsing a valid PDF file."""
        pdf_file = TEST_DATA_DIR / "valid_resume.pdf"
        if not pdf_file.exists():
            pytest.skip(f"Test file {pdf_file} does not exist")

        text = parser.parse(str(pdf_file))
        assert isinstance(text, str)
        assert len(text) > 0
        assert text.strip() != ""
        assert "John Doe" in text or "Test Resume" in text

    def test_parse_multipage_pdf(self, parser: PDFParser):
        """Test parsing a multi-page PDF."""
        pdf_file = TEST_DATA_DIR / "multipage.pdf"
        if not pdf_file.exists():
            pytest.skip(f"Test file {pdf_file} does not exist")

        text = parser.parse(str(pdf_file))
        assert isinstance(text, str)
        assert len(text) > 0

    def test_parsed_text_cleanup(self, parser: PDFParser):
        """Test that parsed text is properly cleaned."""
        pdf_file = TEST_DATA_DIR / "valid_resume.pdf"
        if not pdf_file.exists():
            pytest.skip(f"Test file {pdf_file} does not exist")

        text = parser.parse(str(pdf_file))
        # Check that excessive whitespace is removed
        assert "  " not in text or text.count("  ") < len(text) // 10
        # Check that text has line breaks (structure preserved)
        assert "\n" in text


class TestPDFParserInvalidFiles:
    """Test PDF parser with invalid files."""

    @pytest.fixture
    def parser(self):
        """Create a PDFParser instance."""
        return PDFParser()

    def test_parse_nonexistent_file(self, parser: PDFParser):
        """Test parsing a file that doesn't exist."""
        with pytest.raises(FileNotFoundError):
            parser.parse(str(TEST_DATA_DIR / "nonexistent.pdf"))

    def test_parse_empty_pdf(self, parser: PDFParser):
        """Test parsing an empty PDF file."""
        empty_pdf = TEST_DATA_DIR / "empty.pdf"
        if not empty_pdf.exists():
            pytest.skip(f"Test file {empty_pdf} does not exist")

        with pytest.raises(FileParsingError):
            parser.parse(str(empty_pdf))

    def test_parse_corrupted_pdf(self, parser: PDFParser):
        """Test parsing a corrupted PDF file."""
        corrupted_pdf = TEST_DATA_DIR / "corrupted.pdf"
        if not corrupted_pdf.exists():
            pytest.skip(f"Test file {corrupted_pdf} does not exist")

        with pytest.raises(FileParsingError) as exc_info:
            parser.parse(str(corrupted_pdf))
        assert exc_info.value.original_exception is not None

    def test_parse_text_file_as_pdf(self, parser: PDFParser):
        """Test parsing a text file with .pdf extension."""
        fake_pdf = TEST_DATA_DIR / "fake.pdf"
        if not fake_pdf.exists():
            pytest.skip(f"Test file {fake_pdf} does not exist")

        with pytest.raises(FileParsingError):
            parser.parse(str(fake_pdf))

    def test_parse_non_pdf_file(self, parser: PDFParser):
        """Test parsing a non-PDF file."""
        non_pdf = TEST_DATA_DIR / "sample.txt"
        if not non_pdf.exists():
            pytest.skip(f"Test file {non_pdf} does not exist")

        with pytest.raises(FileParsingError):
            parser.parse(str(non_pdf))

    def test_parse_directory(self, parser: PDFParser):
        """Test parsing a directory path."""
        with pytest.raises(FileParsingError):
            parser.parse(str(TEST_DATA_DIR))


class TestPDFParserSupportsFormat:
    """Test PDF parser format support checking."""

    @pytest.fixture
    def parser(self):
        """Create a PDFParser instance."""
        return PDFParser()

    def test_supports_pdf_extension(self, parser: PDFParser):
        """Test that .pdf extension is supported."""
        assert parser.supports_format("test.pdf")
        assert parser.supports_format("TEST.PDF")
        assert parser.supports_format("/path/to/file.pdf")

    def test_does_not_support_other_extensions(self, parser: PDFParser):
        """Test that non-PDF extensions are not supported."""
        assert not parser.supports_format("test.docx")
        assert not parser.supports_format("test.txt")
        assert not parser.supports_format("test.doc")
        assert not parser.supports_format("test.xlsx")
        assert not parser.supports_format("test")

    def test_supports_format_with_path_object(self, parser: PDFParser):
        """Test supports_format with Path object."""
        assert parser.supports_format(Path("test.pdf"))
        assert not parser.supports_format(Path("test.docx"))


class TestPDFParserEdgeCases:
    """Test PDF parser edge cases."""

    @pytest.fixture
    def parser(self):
        """Create a PDFParser instance."""
        return PDFParser()

    def test_parse_pdf_with_images_only(self, parser: PDFParser):
        """Test parsing a PDF with only images (no text)."""
        image_pdf = TEST_DATA_DIR / "images_only.pdf"
        if not image_pdf.exists():
            pytest.skip(f"Test file {image_pdf} does not exist")

        with pytest.raises(FileParsingError) as exc_info:
            parser.parse(str(image_pdf))
        assert "No text content found in PDF" in str(exc_info.value)

    def test_parse_password_protected_pdf(self, parser: PDFParser):
        """Test parsing a password-protected PDF."""
        protected_pdf = TEST_DATA_DIR / "password_protected.pdf"
        if not protected_pdf.exists():
            pytest.skip(f"Test file {protected_pdf} does not exist")

        with pytest.raises(FileParsingError):
            parser.parse(str(protected_pdf))

    def test_parse_pdf_with_special_characters(self, parser: PDFParser):
        """Test parsing a PDF with special characters."""
        special_pdf = TEST_DATA_DIR / "special_chars.pdf"
        if not special_pdf.exists():
            pytest.skip(f"Test file {special_pdf} does not exist")

        text = parser.parse(str(special_pdf))
        assert isinstance(text, str)
        assert len(text) > 0

    def test_parse_pdf_with_tables(self, parser: PDFParser):
        """Test parsing a PDF with tables."""
        table_pdf = TEST_DATA_DIR / "with_tables.pdf"
        if not table_pdf.exists():
            pytest.skip(f"Test file {table_pdf} does not exist")

        text = parser.parse(str(table_pdf))
        assert isinstance(text, str)
        assert len(text) > 0

    def test_parse_very_large_pdf(self, parser: PDFParser):
        """Test parsing a very large PDF file."""
        large_pdf = TEST_DATA_DIR / "large.pdf"
        if not large_pdf.exists():
            pytest.skip(f"Test file {large_pdf} does not exist")

        text = parser.parse(str(large_pdf))
        assert isinstance(text, str)
        assert len(text) > 1000  # Should have substantial content

    def test_parse_multicolumn_pdf(self, parser: PDFParser):
        """Both column texts extracted in left-before-right reading order."""
        pdf = TEST_DATA_DIR / "multicolumn.pdf"
        if not pdf.exists():
            pytest.skip(f"Test file {pdf} does not exist")

        text = parser.parse(str(pdf))
        assert "Left Column Content" in text
        assert "Right Column Content" in text
        assert text.index("Left Column Content") < text.index("Right Column Content")

    def test_parse_pdf_header_footer_excluded_from_body(self, parser: PDFParser):
        """Body content is present; header/footer bands are cropped out."""
        pdf = TEST_DATA_DIR / "with_header_footer.pdf"
        if not pdf.exists():
            pytest.skip(f"Test file {pdf} does not exist")

        text = parser.parse(str(pdf))
        assert "Main Body Content" in text
        assert "Document Header" not in text
        assert "Page 1 of 1" not in text

    def test_parse_pdf_tables_pipe_delimited(self, parser: PDFParser):
        """Tables in PDFs are extracted as pipe-delimited rows."""
        pdf = TEST_DATA_DIR / "with_tables.pdf"
        if not pdf.exists():
            pytest.skip(f"Test file {pdf} does not exist")

        text = parser.parse(str(pdf))
        assert "|" in text

    def test_encrypted_pdf_raises_informative_error(self, parser: PDFParser):
        """Password-protected PDF raises FileParsingError mentioning encryption."""
        pdf = TEST_DATA_DIR / "password_protected.pdf"
        if not pdf.exists():
            pytest.skip(f"Test file {pdf} does not exist")

        with pytest.raises(FileParsingError) as exc_info:
            parser.parse(str(pdf))
        msg = str(exc_info.value).lower()
        assert "encrypt" in msg or "password" in msg

    def test_image_only_pdf_raises_informative_error(self, parser: PDFParser):
        """Image-only PDF raises FileParsingError mentioning images."""
        pdf = TEST_DATA_DIR / "images_only.pdf"
        if not pdf.exists():
            pytest.skip(f"Test file {pdf} does not exist")

        with pytest.raises(FileParsingError) as exc_info:
            parser.parse(str(pdf))
        assert "image" in str(exc_info.value).lower() or "No text content" in str(exc_info.value)

    def test_clean_extracted_text_empty_string(self, parser: PDFParser):
        """Test _clean_extracted_text with empty string."""
        result = parser._clean_extracted_text("")
        assert result == ""

    def test_clean_extracted_text_whitespace_only(self, parser: PDFParser):
        """Test _clean_extracted_text with whitespace only."""
        result = parser._clean_extracted_text("   \n   \n   ")
        assert result == ""

    def test_clean_extracted_text_with_excessive_spaces(self, parser: PDFParser):
        """Test _clean_extracted_text with excessive spaces."""
        text = "Hello    world\nThis   is    a   test"
        result = parser._clean_extracted_text(text)
        assert "Hello world" in result
        assert "This is a test" in result
        assert "    " not in result

    def test_clean_extracted_text_preserves_line_breaks(self, parser: PDFParser):
        """Test that _clean_extracted_text preserves line breaks."""
        text = "Line 1\nLine 2\nLine 3"
        result = parser._clean_extracted_text(text)
        assert result.count("\n") == 2
        assert "Line 1" in result
        assert "Line 2" in result
        assert "Line 3" in result


class TestPDFParserLayoutMethods:
    """Unit tests for the private layout-analysis methods."""

    @pytest.fixture
    def parser(self):
        return PDFParser()

    def test_split_columns_single_column(self, parser: PDFParser):
        """Words with no large horizontal gap → single column."""
        words = [
            {"x0": 72, "x1": 120, "top": 100, "bottom": 112, "text": "Hello"},
            {"x0": 125, "x1": 170, "top": 100, "bottom": 112, "text": "World"},
            {"x0": 72, "x1": 130, "top": 115, "bottom": 127, "text": "Second"},
        ]
        cols = parser._split_columns(words, page_width=612)
        assert len(cols) == 1
        assert len(cols[0]) == 3

    def test_split_columns_two_columns(self, parser: PDFParser):
        """Words with a wide x gap are split into two columns."""
        left = [
            {"x0": 72, "x1": 200, "top": 100, "bottom": 112, "text": "Left"},
            {"x0": 72, "x1": 210, "top": 115, "bottom": 127, "text": "Column"},
        ]
        right = [
            {"x0": 320, "x1": 450, "top": 100, "bottom": 112, "text": "Right"},
            {"x0": 320, "x1": 470, "top": 115, "bottom": 127, "text": "Column"},
        ]
        cols = parser._split_columns(left + right, page_width=612)
        assert len(cols) == 2
        # Left column words appear first
        assert cols[0][0]["text"] == "Left"
        assert cols[1][0]["text"] == "Right"

    def test_split_columns_empty_words(self, parser: PDFParser):
        """Empty word list returns empty list without error."""
        assert parser._split_columns([], page_width=612) == []

    def test_words_to_lines_single_line(self, parser: PDFParser):
        """Words on the same Y position are joined into one line."""
        words = [
            {"top": 100.0, "text": "John"},
            {"top": 100.5, "text": "Doe"},  # within tolerance
            {"top": 100.0, "text": "Engineer"},
        ]
        result = parser._words_to_lines(words)
        assert result == "John Doe Engineer"

    def test_words_to_lines_multiple_lines(self, parser: PDFParser):
        """Words with distinct Y positions form separate lines."""
        words = [
            {"top": 100.0, "text": "Line1"},
            {"top": 115.0, "text": "Line2"},
            {"top": 130.0, "text": "Line3"},
        ]
        result = parser._words_to_lines(words)
        assert result == "Line1\nLine2\nLine3"

    def test_words_to_lines_empty(self, parser: PDFParser):
        """Empty word list returns empty string."""
        assert parser._words_to_lines([]) == ""

    def test_header_footer_boundaries_proportion(self, parser: PDFParser):
        """Boundaries are 6% from each edge by default."""
        import pdfplumber

        with pdfplumber.open(
            str(
                __import__("pathlib").Path(__file__).parent
                / "data"
                / "valid_resume.pdf"
            )
        ) as pdf:
            page = pdf.pages[0]
            header_end, footer_start = parser._header_footer_boundaries(page)
            assert header_end == pytest.approx(page.height * 0.06, rel=0.01)
            assert footer_start == pytest.approx(page.height * 0.94, rel=0.01)

    def test_inside_any_word_inside_bbox(self, parser: PDFParser):
        """Word midpoint inside a bbox returns True."""
        word = {"x0": 90, "x1": 150, "top": 90, "bottom": 110}
        bboxes = [(80, 80, 200, 120)]
        assert parser._inside_any(word, bboxes) is True

    def test_inside_any_word_outside_bbox(self, parser: PDFParser):
        """Word midpoint outside all bboxes returns False."""
        word = {"x0": 300, "x1": 400, "top": 300, "bottom": 320}
        bboxes = [(80, 80, 200, 120)]
        assert parser._inside_any(word, bboxes) is False

    def test_inside_any_empty_bboxes(self, parser: PDFParser):
        """No bboxes → always False."""
        word = {"x0": 90, "x1": 150, "top": 90, "bottom": 110}
        assert parser._inside_any(word, []) is False
