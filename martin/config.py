"""
Configuration module for Martin

Handles DSPy language model configuration and other system settings.
"""

import os
from typing import Optional

import dspy


class Config:
    """Configuration class for Martin system."""

    def __init__(self):
        # DSPy model configuration
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.model_name = os.getenv("DSPY_MODEL", "openai/gpt-4o-mini")
        self.max_tokens = int(os.getenv("DSPY_MAX_TOKENS", "2000"))
        self.temperature = float(os.getenv("DSPY_TEMPERATURE", "0.1"))
        self.base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

        # Literature search configuration
        self.semantic_scholar_api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
        self.literature_max_results = int(os.getenv("LITERATURE_MAX_RESULTS", "10"))

    def setup_dspy_lm(self) -> None:
        """
        Configure DSPy language model with OpenRouter API.

        OpenRouter provides access to various models including GPT-4, Claude,
        and other open-source models through a unified API.

        Raises:
            ValueError: If OPENROUTER_API_KEY is not set
        """
        if not self.openrouter_api_key:
            raise ValueError(
                "😅 Hey! I need an API key to get started. Could you help me out by setting up your OPENROUTER_API_KEY? "
                "You can grab one at https://openrouter.ai/keys - it's quick and free! "
                "(OPENROUTER_API_KEY environment variable is required)"
            )

        try:
            # Configure DSPy with OpenRouter (using correct LM interface)
            lm = dspy.LM(
                model=self.model_name,
                api_key=self.openrouter_api_key,
                api_base=self.base_url,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )

            dspy.configure(lm=lm)
            print(f"DSPy configured with OpenRouter model: {self.model_name}")

            # Test the model with a simple call to catch issues early
            self._test_model_functionality()

        except Exception as e:
            # Provide clear error messages for common issues
            error_msg = str(e)

            if "not a valid model ID" in error_msg:
                raise ValueError(
                    f"🤔 Hmm, I don't recognize the model '{self.model_name}' - it might not be available on OpenRouter. "
                    f"No worries though! Here are some great options that work perfectly with me:\n"
                    f"  - openai/gpt-4o-mini (my personal favorite!)\n"
                    f"  - openai/gpt-4\n"
                    f"  - openai/gpt-3.5-turbo\n\n"
                    f"Could you update your .env file with one of these? (Invalid model ID: '{self.model_name}')"
                )
            elif "API key" in error_msg or "authentication" in error_msg.lower():
                raise ValueError(
                    f"😅 Looks like there's an issue with my API key. Could you double-check your OPENROUTER_API_KEY in the .env file? "
                    f"If you need a new one, you can grab it at https://openrouter.ai/keys - it's super quick! "
                    f"(Authentication failed)"
                )
            elif "structured output format" in error_msg:
                raise ValueError(
                    f"🤖 Oh! The model '{self.model_name}' doesn't quite speak my language - I need models that support structured output "
                    f"to give you the best analysis possible. Here are some fantastic alternatives that work great with me:\n"
                    f"  - openai/gpt-4o-mini (highly recommended!)\n"
                    f"  - openai/gpt-4\n"
                    f"  - openai/gpt-3.5-turbo\n\n"
                    f"Could you switch to one of these? (Model does not support structured output)"
                )
            else:
                raise ValueError(
                    f"😔 I'm having trouble setting up the model '{self.model_name}'. Let me help you troubleshoot this! "
                    f"Could you check:\n"
                    f"1. Your OPENROUTER_API_KEY is valid and working\n"
                    f"2. The model name is spelled correctly\n"
                    f"3. You have access to this specific model\n\n"
                    f"Don't worry - we'll get this sorted out! (Error: {error_msg})"
                )

    def _test_model_functionality(self) -> None:
        """Test that the model works with DSPy signatures."""
        try:
            # Test with a simple signature to ensure the model works
            class TestSignature(dspy.Signature):
                input_text: str = dspy.InputField()
                output: str = dspy.OutputField()

            test_module = dspy.Predict(TestSignature)
            result = test_module(input_text="Hello, this is a test")

            if not result.output or len(result.output.strip()) == 0:
                raise Exception(
                    "🤔 The model seems a bit quiet - it's not giving me any responses. This might be a temporary issue!"
                )

        except Exception as e:
            error_msg = str(e)
            if "structured output format" in error_msg:
                raise Exception(
                    f"🤖 This model doesn't support the structured output format I need to give you great analysis. Let's try a different one!"
                )
            else:
                raise Exception(
                    f"😅 I'm having trouble testing the model functionality, but don't worry - we can figure this out! ({error_msg})"
                )

    def validate_model_compatibility(self) -> bool:
        """
        Test if the configured model works with DSPy signatures.

        Returns:
            bool: True if model is compatible, False otherwise
        """
        try:
            # Simple test signature
            class TestSignature(dspy.Signature):
                input_text: str = dspy.InputField()
                output: str = dspy.OutputField()

            test_module = dspy.Predict(TestSignature)
            result = test_module(input_text="test")
            return True

        except Exception as e:
            print(f"Model compatibility test failed: {e}")
            return False


# Global configuration instance
config = Config()
