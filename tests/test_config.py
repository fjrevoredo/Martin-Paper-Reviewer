"""
Tests for configuration module.

Tests Config class initialization, validation, and DSPy setup functionality.
"""

import os
from unittest.mock import Mock, patch

import pytest

from martin.config import Config, config


class TestConfigInitialization:
    """Test cases for Config class initialization."""

    def test_config_initialization_with_defaults(self):
        """Test Config initialization with default values."""
        with patch.dict(os.environ, {}, clear=True):
            test_config = Config()

            assert test_config.openrouter_api_key is None
            assert test_config.model_name == "openai/gpt-4o-mini"
            assert test_config.max_tokens == 2000
            assert test_config.temperature == 0.1
            assert test_config.base_url == "https://openrouter.ai/api/v1"
            assert test_config.semantic_scholar_api_key is None
            assert test_config.literature_max_results == 10

    def test_config_initialization_with_environment_variables(self):
        """Test Config initialization with environment variables set."""
        env_vars = {
            "OPENROUTER_API_KEY": "test-openrouter-key",
            "DSPY_MODEL": "openai/gpt-4",
            "DSPY_MAX_TOKENS": "4000",
            "DSPY_TEMPERATURE": "0.2",
            "OPENROUTER_BASE_URL": "https://custom.openrouter.ai/api/v1",
            "SEMANTIC_SCHOLAR_API_KEY": "test-ss-key",
            "LITERATURE_MAX_RESULTS": "20",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            test_config = Config()

            assert test_config.openrouter_api_key == "test-openrouter-key"
            assert test_config.model_name == "openai/gpt-4"
            assert test_config.max_tokens == 4000
            assert test_config.temperature == 0.2
            assert test_config.base_url == "https://custom.openrouter.ai/api/v1"
            assert test_config.semantic_scholar_api_key == "test-ss-key"
            assert test_config.literature_max_results == 20

    def test_config_initialization_with_partial_environment_variables(self):
        """Test Config initialization with some environment variables set."""
        env_vars = {
            "OPENROUTER_API_KEY": "test-key",
            "DSPY_MODEL": "openai/gpt-3.5-turbo",
            # Other variables use defaults
        }

        with patch.dict(os.environ, env_vars, clear=True):
            test_config = Config()

            assert test_config.openrouter_api_key == "test-key"
            assert test_config.model_name == "openai/gpt-3.5-turbo"
            assert test_config.max_tokens == 2000  # Default
            assert test_config.temperature == 0.1  # Default
            assert test_config.semantic_scholar_api_key is None  # Default

    def test_config_type_conversion(self):
        """Test that environment variables are properly converted to correct types."""
        env_vars = {
            "DSPY_MAX_TOKENS": "3000",
            "DSPY_TEMPERATURE": "0.5",
            "LITERATURE_MAX_RESULTS": "15",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            test_config = Config()

            assert isinstance(test_config.max_tokens, int)
            assert test_config.max_tokens == 3000
            assert isinstance(test_config.temperature, float)
            assert test_config.temperature == 0.5
            assert isinstance(test_config.literature_max_results, int)
            assert test_config.literature_max_results == 15

    def test_config_invalid_numeric_values(self):
        """Test Config handles invalid numeric environment variables."""
        env_vars = {
            "DSPY_MAX_TOKENS": "not-a-number",
            "DSPY_TEMPERATURE": "invalid-float",
            "LITERATURE_MAX_RESULTS": "not-an-int",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            # Should raise ValueError when trying to convert invalid values
            with pytest.raises(ValueError):
                Config()


class TestConfigDSPySetup:
    """Test cases for DSPy language model setup."""

    @patch("dspy.configure")
    @patch("dspy.LM")
    def test_setup_dspy_lm_success(self, mock_lm, mock_configure):
        """Test successful DSPy language model setup."""
        # Mock the LM instance
        mock_lm_instance = Mock()
        mock_lm.return_value = mock_lm_instance

        env_vars = {"OPENROUTER_API_KEY": "test-api-key"}

        with patch.dict(os.environ, env_vars, clear=True):
            test_config = Config()

            # Mock the test functionality to avoid actual API calls
            with patch.object(test_config, "_test_model_functionality"):
                test_config.setup_dspy_lm()

            # Verify LM was created with correct parameters
            mock_lm.assert_called_once_with(
                model="openai/gpt-4o-mini",
                api_key="test-api-key",
                api_base="https://openrouter.ai/api/v1",
                max_tokens=2000,
                temperature=0.1,
            )

            # Verify DSPy was configured with the LM instance
            mock_configure.assert_called_once_with(lm=mock_lm_instance)

    @patch("dspy.configure")
    @patch("dspy.LM")
    def test_setup_dspy_lm_with_custom_settings(self, mock_lm, mock_configure):
        """Test DSPy setup with custom configuration settings."""
        mock_lm_instance = Mock()
        mock_lm.return_value = mock_lm_instance

        env_vars = {
            "OPENROUTER_API_KEY": "custom-key",
            "DSPY_MODEL": "openai/gpt-4",
            "DSPY_MAX_TOKENS": "4000",
            "DSPY_TEMPERATURE": "0.3",
            "OPENROUTER_BASE_URL": "https://custom.api.com/v1",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            test_config = Config()

            with patch.object(test_config, "_test_model_functionality"):
                test_config.setup_dspy_lm()

            mock_lm.assert_called_once_with(
                model="openai/gpt-4",
                api_key="custom-key",
                api_base="https://custom.api.com/v1",
                max_tokens=4000,
                temperature=0.3,
            )

    def test_setup_dspy_lm_missing_api_key(self):
        """Test DSPy setup fails with missing API key."""
        with patch.dict(os.environ, {}, clear=True):
            test_config = Config()

            with pytest.raises(ValueError) as exc_info:
                test_config.setup_dspy_lm()

            error_message = str(exc_info.value)
            assert (
                "OPENROUTER_API_KEY environment variable is required" in error_message
            )
            assert "https://openrouter.ai/keys" in error_message

    @patch("dspy.configure")
    @patch("dspy.LM")
    def test_setup_dspy_lm_invalid_model_error(self, mock_lm, mock_configure):
        """Test DSPy setup handles invalid model ID error."""
        mock_lm.side_effect = Exception("not a valid model ID")

        env_vars = {"OPENROUTER_API_KEY": "test-key"}

        with patch.dict(os.environ, env_vars, clear=True):
            test_config = Config()

            with pytest.raises(ValueError) as exc_info:
                test_config.setup_dspy_lm()

            error_message = str(exc_info.value)
            assert "Invalid model ID" in error_message
            assert "openai/gpt-4o-mini" in error_message
            assert "openai/gpt-4" in error_message
            assert "openai/gpt-3.5-turbo" in error_message

    @patch("dspy.configure")
    @patch("dspy.LM")
    def test_setup_dspy_lm_authentication_error(self, mock_lm, mock_configure):
        """Test DSPy setup handles authentication error."""
        mock_lm.side_effect = Exception("API key authentication failed")

        env_vars = {"OPENROUTER_API_KEY": "invalid-key"}

        with patch.dict(os.environ, env_vars, clear=True):
            test_config = Config()

            with pytest.raises(ValueError) as exc_info:
                test_config.setup_dspy_lm()

            error_message = str(exc_info.value)
            assert "Authentication failed" in error_message
            assert "OPENROUTER_API_KEY" in error_message
            assert "https://openrouter.ai/keys" in error_message

    @patch("dspy.configure")
    @patch("dspy.LM")
    def test_setup_dspy_lm_structured_output_error(self, mock_lm, mock_configure):
        """Test DSPy setup handles structured output format error."""
        mock_lm.side_effect = Exception("structured output format not supported")

        env_vars = {"OPENROUTER_API_KEY": "test-key"}

        with patch.dict(os.environ, env_vars, clear=True):
            test_config = Config()

            with pytest.raises(ValueError) as exc_info:
                test_config.setup_dspy_lm()

            error_message = str(exc_info.value)
            assert "doesn't quite speak my language" in error_message
            assert "🤖" in error_message
            assert "openai/gpt-4" in error_message

    @patch("dspy.configure")
    @patch("dspy.LM")
    def test_setup_dspy_lm_generic_error(self, mock_lm, mock_configure):
        """Test DSPy setup handles generic errors."""
        mock_lm.side_effect = Exception("Some unexpected error")

        env_vars = {"OPENROUTER_API_KEY": "test-key"}

        with patch.dict(os.environ, env_vars, clear=True):
            test_config = Config()

            with pytest.raises(ValueError) as exc_info:
                test_config.setup_dspy_lm()

            error_message = str(exc_info.value)
            assert "I'm having trouble setting up the model" in error_message
            assert "Some unexpected error" in error_message
            assert "OPENROUTER_API_KEY is valid" in error_message


class TestConfigModelTesting:
    """Test cases for model functionality testing."""

    @patch("dspy.Predict")
    def test_test_model_functionality_success(self, mock_predict):
        """Test successful model functionality test."""
        # Mock successful prediction
        mock_instance = Mock()
        mock_result = Mock()
        mock_result.output = "Test response"
        mock_instance.return_value = mock_result
        mock_predict.return_value = mock_instance

        env_vars = {"OPENROUTER_API_KEY": "test-key"}

        with patch.dict(os.environ, env_vars, clear=True):
            test_config = Config()

            # Should not raise any exception
            test_config._test_model_functionality()

            # Verify the test signature was created and called
            mock_predict.assert_called_once()
            mock_instance.assert_called_once_with(input_text="Hello, this is a test")

    @patch("dspy.Predict")
    def test_test_model_functionality_empty_response(self, mock_predict):
        """Test model functionality test with empty response."""
        mock_instance = Mock()
        mock_result = Mock()
        mock_result.output = ""  # Empty response
        mock_instance.return_value = mock_result
        mock_predict.return_value = mock_instance

        env_vars = {"OPENROUTER_API_KEY": "test-key"}

        with patch.dict(os.environ, env_vars, clear=True):
            test_config = Config()

            with pytest.raises(Exception) as exc_info:
                test_config._test_model_functionality()

            assert "I'm having trouble testing the model functionality" in str(
                exc_info.value
            )

    @patch("dspy.Predict")
    def test_test_model_functionality_structured_output_error(self, mock_predict):
        """Test model functionality test with structured output error."""
        mock_predict.side_effect = Exception("structured output format not supported")

        env_vars = {"OPENROUTER_API_KEY": "test-key"}

        with patch.dict(os.environ, env_vars, clear=True):
            test_config = Config()

            with pytest.raises(Exception) as exc_info:
                test_config._test_model_functionality()

            error_message = str(exc_info.value)
            assert "doesn't support the structured output format" in error_message
            assert "🤖" in error_message

    @patch("dspy.Predict")
    def test_test_model_functionality_generic_error(self, mock_predict):
        """Test model functionality test with generic error."""
        mock_predict.side_effect = Exception("Some model error")

        env_vars = {"OPENROUTER_API_KEY": "test-key"}

        with patch.dict(os.environ, env_vars, clear=True):
            test_config = Config()

            with pytest.raises(Exception) as exc_info:
                test_config._test_model_functionality()

            error_message = str(exc_info.value)
            assert "I'm having trouble testing the model functionality" in error_message
            assert "Some model error" in error_message


class TestConfigModelCompatibility:
    """Test cases for model compatibility validation."""

    @patch("dspy.Predict")
    def test_validate_model_compatibility_success(self, mock_predict):
        """Test successful model compatibility validation."""
        mock_instance = Mock()
        mock_result = Mock()
        mock_result.output = "Test response"
        mock_instance.return_value = mock_result
        mock_predict.return_value = mock_instance

        env_vars = {"OPENROUTER_API_KEY": "test-key"}

        with patch.dict(os.environ, env_vars, clear=True):
            test_config = Config()

            result = test_config.validate_model_compatibility()

            assert result is True
            mock_predict.assert_called_once()
            mock_instance.assert_called_once_with(input_text="test")

    @patch("dspy.Predict")
    def test_validate_model_compatibility_failure(self, mock_predict):
        """Test model compatibility validation failure."""
        mock_predict.side_effect = Exception("Model compatibility error")

        env_vars = {"OPENROUTER_API_KEY": "test-key"}

        with patch.dict(os.environ, env_vars, clear=True):
            test_config = Config()

            result = test_config.validate_model_compatibility()

            assert result is False


class TestGlobalConfigInstance:
    """Test cases for the global config instance."""

    def test_global_config_instance_exists(self):
        """Test that global config instance is available."""
        from martin.config import config

        assert config is not None
        assert isinstance(config, Config)

    def test_global_config_instance_attributes(self):
        """Test that global config instance has expected attributes."""
        from martin.config import config

        # Test that all expected attributes exist
        assert hasattr(config, "openrouter_api_key")
        assert hasattr(config, "model_name")
        assert hasattr(config, "max_tokens")
        assert hasattr(config, "temperature")
        assert hasattr(config, "base_url")
        assert hasattr(config, "semantic_scholar_api_key")
        assert hasattr(config, "literature_max_results")

        # Test that methods exist
        assert hasattr(config, "setup_dspy_lm")
        assert hasattr(config, "validate_model_compatibility")


class TestConfigEdgeCases:
    """Test edge cases and error conditions for Config class."""

    def test_config_with_empty_string_environment_variables(self):
        """Test Config handles empty string environment variables."""
        env_vars = {
            "OPENROUTER_API_KEY": "",
            "DSPY_MODEL": "",
            "SEMANTIC_SCHOLAR_API_KEY": "",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            test_config = Config()

            # Empty strings should be treated as None/defaults
            assert test_config.openrouter_api_key == ""
            assert test_config.model_name == ""  # Will use empty string, not default
            assert test_config.semantic_scholar_api_key == ""

    def test_config_with_whitespace_environment_variables(self):
        """Test Config handles whitespace in environment variables."""
        env_vars = {
            "OPENROUTER_API_KEY": "  test-key  ",
            "DSPY_MODEL": "  openai/gpt-4  ",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            test_config = Config()

            # Should preserve whitespace (real usage would trim these)
            assert test_config.openrouter_api_key == "  test-key  "
            assert test_config.model_name == "  openai/gpt-4  "

    def test_config_numeric_boundary_values(self):
        """Test Config with boundary numeric values."""
        env_vars = {
            "DSPY_MAX_TOKENS": "1",
            "DSPY_TEMPERATURE": "0.0",
            "LITERATURE_MAX_RESULTS": "100",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            test_config = Config()

            assert test_config.max_tokens == 1
            assert test_config.temperature == 0.0
            assert test_config.literature_max_results == 100

    def test_config_negative_numeric_values(self):
        """Test Config with negative numeric values."""
        env_vars = {
            "DSPY_MAX_TOKENS": "-1000",
            "DSPY_TEMPERATURE": "-0.5",
            "LITERATURE_MAX_RESULTS": "-10",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            test_config = Config()

            # Should accept negative values (validation would happen elsewhere)
            assert test_config.max_tokens == -1000
            assert test_config.temperature == -0.5
            assert test_config.literature_max_results == -10
