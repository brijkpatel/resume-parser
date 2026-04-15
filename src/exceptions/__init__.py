"""All custom exceptions for the resume parser."""

from typing import Optional


class ResumeParserException(Exception):
    """Base exception for every resume-parser error."""

    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        self.message = message
        self.original_exception = original_exception
        super().__init__(self.message)


# ---------------------------------------------------------------------------
# File / parsing layer
# ---------------------------------------------------------------------------


class FileParsingError(ResumeParserException):
    """Raised when a file cannot be parsed."""


class UnsupportedFileFormatError(ResumeParserException):
    """Raised when the file format is not supported."""


# ---------------------------------------------------------------------------
# Field extraction layer
# ---------------------------------------------------------------------------


class FieldExtractionError(ResumeParserException):
    """Raised when a field extractor fails."""


class InvalidConfigurationError(ResumeParserException):
    """Raised when the extractor / framework is misconfigured."""


# ---------------------------------------------------------------------------
# Strategy layer
# ---------------------------------------------------------------------------


class StrategyExtractionError(ResumeParserException):
    """Raised when a strategy fails to extract a field."""


class NoMatchFoundError(StrategyExtractionError):
    """Raised when a strategy finds no match in the text."""


class InvalidStrategyConfigError(ResumeParserException):
    """Raised when a strategy is configured incorrectly."""


# ---------------------------------------------------------------------------
# External services
# ---------------------------------------------------------------------------


class ExternalServiceError(ResumeParserException):
    """Raised when an external service call (LLM, NER API, …) fails."""


__all__ = [
    "ResumeParserException",
    "FileParsingError",
    "UnsupportedFileFormatError",
    "FieldExtractionError",
    "InvalidConfigurationError",
    "StrategyExtractionError",
    "NoMatchFoundError",
    "InvalidStrategyConfigError",
    "ExternalServiceError",
]
