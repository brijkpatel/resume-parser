"""Extract text from PDF files using pdfplumber with layout-aware parsing."""

from pathlib import Path
from typing import List, Union

import pdfplumber
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfdocument import PDFPasswordIncorrect
from pdfminer.pdfparser import PDFParser as _PDFMinerParser

from exceptions import FileParsingError
from interfaces.file_parser import FileParser
from utils import logger

# pdfplumber uses a top-left origin: (x0, top, x1, bottom).
# "top" increases downward; "bottom" is further down the page.
# page.height is the full page height in the same units.


class PDFParser(FileParser):
    """Parse PDF files and extract text content with layout awareness.

    Improvements over basic pdfminer extraction:
    - Tables extracted separately and formatted as pipe-delimited rows.
    - Multi-column layouts detected and read in left-to-right column order.
    - Header / footer bands cropped out before body extraction.
    - Encrypted / password-protected PDFs caught with an informative error.
    - Image-only PDFs reported clearly.
    """

    def __init__(self):
        self.supported_extensions = [".pdf"]
        logger.debug("PDFParser initialized")

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def parse(self, file_path: str) -> str:
        """Extract text from a PDF file.

        Args:
            file_path: Path to the PDF file.

        Returns:
            Cleaned, layout-aware text content.

        Raises:
            FileParsingError: If the file cannot be parsed.
        """
        self._validate_file_path(file_path)
        self._check_encryption(file_path)

        try:
            logger.info("Starting PDF parsing: %s", file_path)
            page_texts: List[str] = []

            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = self._extract_page(page)
                    if page_text.strip():
                        page_texts.append(page_text)

            if not page_texts:
                raise FileParsingError(
                    "No text content found in PDF. "
                    "The file may contain only images or scanned content."
                )

            full_text = "\n\n".join(page_texts)
            cleaned = self._clean_extracted_text(full_text)
            logger.info(
                "Successfully parsed PDF: %s (%d characters)", file_path, len(cleaned)
            )
            return cleaned

        except FileParsingError:
            raise
        except Exception as e:
            raise FileParsingError("PDF parsing failed.", original_exception=e) from e

    def supports_format(self, file_path: Union[str, Path]) -> bool:
        """Return True if the file is a PDF."""
        return self._get_file_extension(file_path) in self.supported_extensions

    # ------------------------------------------------------------------
    # Pre-flight check
    # ------------------------------------------------------------------

    def _check_encryption(self, file_path: str) -> None:
        """Raise FileParsingError early if the PDF is encrypted/password-protected."""
        try:
            with open(file_path, "rb") as fh:
                parser = _PDFMinerParser(fh)
                doc = PDFDocument(parser)
                if not doc.is_extractable:
                    raise FileParsingError(
                        "PDF is encrypted or password-protected. "
                        "Decrypt the file or provide the password before parsing."
                    )
        except PDFPasswordIncorrect:
            raise FileParsingError(
                "PDF is password-protected. "
                "Provide the correct password to extract text."
            )
        except FileParsingError:
            raise
        except Exception:
            # Malformed header etc. — let pdfplumber produce a better error.
            pass

    # ------------------------------------------------------------------
    # Per-page extraction
    # ------------------------------------------------------------------

    def _extract_page(self, page: "pdfplumber.page.Page") -> str:  # type: ignore[name-defined]
        """Extract text from a single page with table and column awareness."""
        header_top, footer_top = self._header_footer_boundaries(page)
        body = page.crop((0, header_top, page.width, footer_top))

        # Find table bboxes so we can exclude them from the word flow.
        table_bboxes = [tbl.bbox for tbl in body.find_tables()]

        tables_text = self._extract_tables(body)
        words_text = self._extract_words(body, excluded_bboxes=table_bboxes)

        parts = [p for p in (words_text, tables_text) if p.strip()]
        return "\n".join(parts)

    # ------------------------------------------------------------------
    # Header / footer cropping
    # ------------------------------------------------------------------

    def _header_footer_boundaries(
        self, page: "pdfplumber.page.Page", margin_pct: float = 0.06  # type: ignore[name-defined]
    ) -> tuple:
        """Return (header_bottom, footer_top) as top-origin y coordinates.

        pdfplumber crop coordinates use top-left origin:
          y=0 is the top of the page; y=page.height is the bottom.
        """
        height = page.height
        header_bottom = height * margin_pct        # end of header band (from top)
        footer_top = height * (1.0 - margin_pct)  # start of footer band (from top)
        return header_bottom, footer_top

    # ------------------------------------------------------------------
    # Table extraction
    # ------------------------------------------------------------------

    def _extract_tables(self, page: "pdfplumber.page.Page") -> str:  # type: ignore[name-defined]
        """Extract all tables from a page as pipe-delimited rows."""
        tables = page.extract_tables()
        if not tables:
            return ""
        lines: List[str] = []
        for table in tables:
            for row in table:
                cells = [(cell or "").replace("\n", " ").strip() for cell in row]
                if any(cells):
                    lines.append(" | ".join(cells))
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Word / text flow extraction
    # ------------------------------------------------------------------

    def _extract_words(
        self,
        page: "pdfplumber.page.Page",  # type: ignore[name-defined]
        excluded_bboxes: List[tuple],
    ) -> str:
        """Extract body words respecting multi-column layout.

        Words that fall inside a table bbox are skipped (the table extractor
        already handles those).
        """
        words = page.extract_words(x_tolerance=3, y_tolerance=3)
        if not words:
            return ""

        # Filter out words inside table regions.
        if excluded_bboxes:
            words = [w for w in words if not self._inside_any(w, excluded_bboxes)]
        if not words:
            return ""

        columns = self._split_columns(words, page.width)
        column_texts = [self._words_to_lines(col) for col in columns]
        return "\n".join(t for t in column_texts if t)

    @staticmethod
    def _inside_any(word: dict, bboxes: List[tuple]) -> bool:
        """Return True if the word's midpoint falls inside any of the bboxes."""
        wx = (word["x0"] + word["x1"]) / 2
        wy = (word["top"] + word["bottom"]) / 2
        for x0, top, x1, bottom in bboxes:
            if x0 <= wx <= x1 and top <= wy <= bottom:
                return True
        return False

    @staticmethod
    def _split_columns(words: List[dict], page_width: float) -> List[List[dict]]:
        """Detect column layout by looking for large horizontal gaps.

        Returns a list of word groups, one per detected column, ordered
        left-to-right.
        """
        if not words:
            return []

        # Collect all unique x0 positions and look for wide gaps.
        x0_values = sorted(set(w["x0"] for w in words))
        gap_threshold = page_width * 0.12  # 12% of page width = column gap

        # Find split points: positions where consecutive x0s have a large gap.
        split_xs: List[float] = [0.0]
        for i in range(1, len(x0_values)):
            if x0_values[i] - x0_values[i - 1] >= gap_threshold:
                split_xs.append(x0_values[i])

        if len(split_xs) == 1:
            return [sorted(words, key=lambda w: (w["top"], w["x0"]))]

        # Assign words to columns.
        columns: List[List[dict]] = [[] for _ in split_xs]
        for word in words:
            col_idx = 0
            for i, boundary in enumerate(split_xs):
                if word["x0"] >= boundary:
                    col_idx = i
            columns[col_idx].append(word)

        # Sort each column top-to-bottom, left-to-right within a line.
        for col in columns:
            col.sort(key=lambda w: (w["top"], w["x0"]))

        return [c for c in columns if c]

    @staticmethod
    def _words_to_lines(words: List[dict]) -> str:
        """Group words into lines by Y-proximity and join with spaces."""
        if not words:
            return ""
        lines: List[List[str]] = []
        current_line = [words[0]["text"]]
        current_top = words[0]["top"]
        line_tolerance = 3.0

        for word in words[1:]:
            if abs(word["top"] - current_top) <= line_tolerance:
                current_line.append(word["text"])
            else:
                lines.append(current_line)
                current_line = [word["text"]]
                current_top = word["top"]
        lines.append(current_line)
        return "\n".join(" ".join(line) for line in lines)

    # ------------------------------------------------------------------
    # Text cleaning (unchanged — existing tests pass against this)
    # ------------------------------------------------------------------

    def _clean_extracted_text(self, text: str) -> str:
        """Collapse intra-line excess spaces; preserve line breaks."""
        if not text:
            return ""
        lines: List[str] = []
        for line in text.split("\n"):
            cleaned = " ".join(line.split())
            if cleaned:
                lines.append(cleaned)
        return "\n".join(lines)
