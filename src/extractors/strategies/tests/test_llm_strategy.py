"""Unit tests for LLMExtractionStrategy."""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock

from interfaces.extracting_strategy import FieldSpec, FieldType
from extractors.strategies.llm import LLMExtractionStrategy
from exceptions import (
    InvalidStrategyConfigError,
    NoMatchFoundError,
    ExternalServiceError,
)

# Mocked API key used across all tests — never hits a real Gemini endpoint.
_MOCK_API_KEY = "test-gemini-api-key-mock"


class TestLLMExtractionStrategy:
    """Tests for LLMExtractionStrategy."""

    @pytest.fixture(autouse=True)
    def mock_gemini_env(self):
        """Patch GEMINI_API_KEY and genai.configure for every test so no real
        API credentials are required and no network calls are made."""
        with (
            patch.dict(os.environ, {"GEMINI_API_KEY": _MOCK_API_KEY}),
            patch("extractors.strategies.llm.genai.configure") as mock_configure,
        ):
            self.mock_configure = mock_configure
            yield mock_configure

    # ------------------------------------------------------------------
    # Initialisation tests
    # ------------------------------------------------------------------

    @patch("extractors.strategies.llm.genai.GenerativeModel")
    def test_init_success(self, mock_model_class: MagicMock):
        """Test successful initialization."""
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        spec = FieldSpec(field_type=FieldType.NAME)

        strategy = LLMExtractionStrategy(spec)

        assert strategy.model == mock_model
        assert strategy.spec == spec
        mock_model_class.assert_called_once_with("gemini-2.0-flash")
        self.mock_configure.assert_called_once_with(api_key=_MOCK_API_KEY)

    @patch("extractors.strategies.llm.genai.GenerativeModel")
    def test_init_with_custom_model(self, mock_model_class: MagicMock):
        """Test initialization with a custom model name."""
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        spec = FieldSpec(field_type=FieldType.NAME)

        strategy = LLMExtractionStrategy(spec, model_name="gemini-pro")

        assert strategy.model == mock_model
        assert strategy.spec == spec
        mock_model_class.assert_called_once_with("gemini-pro")

    def test_init_missing_api_key_raises_error(self):
        """Missing GEMINI_API_KEY must raise InvalidStrategyConfigError."""
        spec = FieldSpec(field_type=FieldType.NAME)

        # Remove the key that the autouse fixture injected
        with patch.dict(os.environ, {}, clear=False):
            del os.environ["GEMINI_API_KEY"]
            with pytest.raises(InvalidStrategyConfigError, match="GEMINI_API_KEY"):
                LLMExtractionStrategy(spec)

    @patch("extractors.strategies.llm.genai.GenerativeModel")
    def test_init_model_failure_raises_error(self, mock_model_class: MagicMock):
        """Model init failure must raise InvalidStrategyConfigError."""
        mock_model_class.side_effect = Exception("Model init failed")
        spec = FieldSpec(field_type=FieldType.NAME)

        with pytest.raises(InvalidStrategyConfigError):
            LLMExtractionStrategy(spec)

    # ------------------------------------------------------------------
    # extract() — successful response cases
    # ------------------------------------------------------------------

    @patch("extractors.strategies.llm.genai.GenerativeModel")
    def test_extract_single_value(self, mock_model_class: MagicMock):
        """Plain-text (non-JSON) response treated as single extracted value."""
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "John Doe"
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        spec = FieldSpec(field_type=FieldType.NAME)

        strategy = LLMExtractionStrategy(spec)
        result = strategy.extract("My name is John Doe")

        assert isinstance(result, list)
        assert result == ["John Doe"]

    @patch("extractors.strategies.llm.genai.GenerativeModel")
    def test_extract_multi_value_json(self, mock_model_class: MagicMock):
        """JSON array response with top_k limit applied."""
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = '["Python", "Java", "JavaScript"]'
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        spec = FieldSpec(field_type=FieldType.SKILLS, top_k=2)

        strategy = LLMExtractionStrategy(spec)
        result = strategy.extract("Skills: Python, Java, JavaScript")

        assert result == ["Python", "Java"]

    @patch("extractors.strategies.llm.genai.GenerativeModel")
    def test_extract_json_array_embedded_in_text(self, mock_model_class: MagicMock):
        """JSON array embedded in surrounding prose is still parsed correctly."""
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = 'Here are the skills: ["Python", "Java"] from the text.'
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        spec = FieldSpec(field_type=FieldType.SKILLS, top_k=0)

        strategy = LLMExtractionStrategy(spec)
        result = strategy.extract("Some text")

        assert result == ["Python", "Java"]

    # ------------------------------------------------------------------
    # extract() — error / edge cases
    # ------------------------------------------------------------------

    @patch("extractors.strategies.llm.genai.GenerativeModel")
    def test_extract_empty_text_raises_error(self, mock_model_class: MagicMock):
        """Whitespace-only input raises NoMatchFoundError immediately."""
        mock_model_class.return_value = Mock()
        spec = FieldSpec(field_type=FieldType.NAME)

        strategy = LLMExtractionStrategy(spec)

        with pytest.raises(NoMatchFoundError, match="Cannot extract from empty text"):
            strategy.extract("   ")

    @patch("extractors.strategies.llm.genai.GenerativeModel")
    def test_extract_not_found_sentinel_raises_error(self, mock_model_class: MagicMock):
        """NOT_FOUND sentinel response raises NoMatchFoundError."""
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "NOT_FOUND"
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        spec = FieldSpec(field_type=FieldType.NAME)

        strategy = LLMExtractionStrategy(spec)

        with pytest.raises(NoMatchFoundError, match="LLM could not find field"):
            strategy.extract("Some text")

    @patch("extractors.strategies.llm.genai.GenerativeModel")
    def test_extract_empty_response_raises_error(self, mock_model_class: MagicMock):
        """Empty string from the model raises NoMatchFoundError."""
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = ""
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        spec = FieldSpec(field_type=FieldType.NAME)

        strategy = LLMExtractionStrategy(spec)

        with pytest.raises(NoMatchFoundError, match="LLM returned empty response"):
            strategy.extract("Some text")

    @patch("extractors.strategies.llm.genai.GenerativeModel")
    def test_extract_malformed_json_raises_error(self, mock_model_class: MagicMock):
        """Malformed JSON array raises ExternalServiceError."""
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = '["Python", "Java"'  # missing closing bracket
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        spec = FieldSpec(field_type=FieldType.SKILLS, top_k=0)

        strategy = LLMExtractionStrategy(spec)

        with pytest.raises(ExternalServiceError):
            strategy.extract("Some text")

    @patch("extractors.strategies.llm.genai.GenerativeModel")
    def test_extract_api_failure_raises_error(self, mock_model_class: MagicMock):
        """Network / API error from generate_content raises ExternalServiceError."""
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_model_class.return_value = mock_model
        spec = FieldSpec(field_type=FieldType.NAME)

        strategy = LLMExtractionStrategy(spec)

        with pytest.raises(ExternalServiceError):
            strategy.extract("Some text")

    @patch("extractors.strategies.llm.genai.GenerativeModel")
    def test_extract_empty_json_array_raises_error(self, mock_model_class: MagicMock):
        """Empty JSON array [] raises NoMatchFoundError."""
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "[]"
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        spec = FieldSpec(field_type=FieldType.SKILLS, top_k=0)

        strategy = LLMExtractionStrategy(spec)

        with pytest.raises(NoMatchFoundError, match="LLM found no values"):
            strategy.extract("Some text")

    @patch("extractors.strategies.llm.genai.GenerativeModel")
    def test_extract_non_array_json_raises_error(self, mock_model_class: MagicMock):
        """JSON object (not array) raises ExternalServiceError."""
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = '{"key": "value"}'
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        spec = FieldSpec(field_type=FieldType.SKILLS, top_k=0)

        strategy = LLMExtractionStrategy(spec)

        with pytest.raises(ExternalServiceError):
            strategy.extract("Some text")

    # ------------------------------------------------------------------
    # _build_prompt tests
    # ------------------------------------------------------------------

    @patch("extractors.strategies.llm.genai.GenerativeModel")
    def test_build_prompt_for_name_field(self, mock_model_class: MagicMock):
        """Prompt for NAME field mentions 'full name' and JSON array."""
        mock_model_class.return_value = Mock()
        spec = FieldSpec(field_type=FieldType.NAME)

        strategy = LLMExtractionStrategy(spec)
        prompt = strategy._build_prompt("text", spec)

        assert "full name" in prompt.lower()
        assert "JSON array" in prompt

    @patch("extractors.strategies.llm.genai.GenerativeModel")
    def test_build_prompt_for_skills_field(self, mock_model_class: MagicMock):
        """Prompt for SKILLS field mentions 'skills' and JSON array."""
        mock_model_class.return_value = Mock()
        spec = FieldSpec(field_type=FieldType.SKILLS, top_k=5)

        strategy = LLMExtractionStrategy(spec)
        prompt = strategy._build_prompt("text", spec)

        assert "skills" in prompt.lower()
        assert "JSON array" in prompt
