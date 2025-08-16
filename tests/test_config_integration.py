"""
Integration tests for Martin configuration and setup.

These tests validate that Martin's configuration works correctly
in different environments and with different settings.
"""

import os
import pytest
from unittest.mock import patch, MagicMock


class TestConfigurationIntegration:
    """Test Martin's configuration in realistic scenarios."""
    
    def test_config_with_env_variables(self):
        """Test that configuration loads correctly from environment variables."""
        from martin.config import Config
        
        # Test with mock environment variables
        test_env = {
            "OPENROUTER_API_KEY": "test-key-123",
            "DSPY_MODEL": "openai/gpt-4o-mini",
            "DSPY_MAX_TOKENS": "1500",
            "DSPY_TEMPERATURE": "0.1"
        }
        
        with patch.dict(os.environ, test_env, clear=False):
            config = Config()
            
            assert config.openrouter_api_key == "test-key-123"
            assert config.model_name == "openai/gpt-4o-mini"
            assert config.max_tokens == 1500
            assert config.temperature == 0.1
    
    def test_config_defaults(self):
        """Test that configuration uses appropriate defaults."""
        from martin.config import Config
        
        # Test with minimal environment
        test_env = {
            "OPENROUTER_API_KEY": "test-key"
        }
        
        with patch.dict(os.environ, test_env, clear=True):
            config = Config()
            
            assert config.openrouter_api_key == "test-key"
            assert config.model_name == "openai/gpt-4o-mini"  # Default
            assert config.max_tokens == 2000  # Default
            assert config.temperature == 0.1  # Default
    
    @pytest.mark.skipif(
        not os.getenv("OPENROUTER_API_KEY"),
        reason="OPENROUTER_API_KEY not available"
    )
    def test_dspy_setup_with_real_api_key(self):
        """Test DSPy setup with real API key."""
        from martin.config import config
        
        # This should not raise an exception
        config.setup_dspy_lm()
        
        # Verify DSPy is configured
        import dspy
        assert dspy.settings.lm is not None, "DSPy language model should be configured"
    
    def test_dspy_setup_without_api_key(self):
        """Test that DSPy setup fails gracefully without API key."""
        from martin.config import Config
        
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            
            with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
                config.setup_dspy_lm()


class TestPaperReviewerIntegration:
    """Test PaperReviewer initialization and basic setup."""
    
    @pytest.mark.skipif(
        not os.getenv("OPENROUTER_API_KEY"),
        reason="OPENROUTER_API_KEY not available"
    )
    def test_paper_reviewer_initialization(self):
        """Test that PaperReviewer can be initialized correctly."""
        from martin.paper_reviewer import PaperReviewer
        from martin.config import config
        
        # Configure DSPy first
        config.setup_dspy_lm()
        
        # Create reviewer with different configurations
        reviewer1 = PaperReviewer()
        assert reviewer1.max_search_results == 5  # Default
        assert reviewer1.enable_social_media == True  # Default
        
        reviewer2 = PaperReviewer(
            max_search_results=2,
            enable_social_media=False,
            verbose=True
        )
        assert reviewer2.max_search_results == 2
        assert reviewer2.enable_social_media == False
        assert reviewer2.verbose == True
    
    def test_paper_reviewer_without_dspy_config(self):
        """Test PaperReviewer behavior without DSPy configuration."""
        from martin.paper_reviewer import PaperReviewer
        
        # Reset DSPy configuration
        import dspy
        dspy.settings.configure(lm=None)
        
        # Should be able to create reviewer, but forward() will fail
        reviewer = PaperReviewer()
        assert reviewer is not None
        
        # Attempting to use it should fail gracefully
        with pytest.raises(Exception):  # Could be various exceptions
            reviewer.forward("https://example.com/test.pdf")


class TestSystemIntegration:
    """Test system-level integration scenarios."""
    
    @pytest.mark.skipif(
        not os.getenv("OPENROUTER_API_KEY"),
        reason="OPENROUTER_API_KEY not available"
    )
    def test_full_system_smoke_test(self):
        """Smoke test for the complete Martin system."""
        from martin.paper_reviewer import PaperReviewer
        from martin.config import config
        from martin.models.paper_text import PaperText
        
        # Test configuration
        config.setup_dspy_lm()
        
        # Test model creation
        paper_text = PaperText(full_text="Test paper content")
        assert paper_text.full_text == "Test paper content"
        
        # Test reviewer creation
        reviewer = PaperReviewer(
            max_search_results=1,
            enable_social_media=False,
            verbose=False
        )
        
        # Test that all components are properly initialized
        assert reviewer.pdf_extractor is not None
        assert reviewer.academic_search is not None
        assert hasattr(reviewer, 'extraction')
        assert hasattr(reviewer, 'methodology')
        assert hasattr(reviewer, 'contributions')
        
        print("✅ System smoke test passed")
    
    def test_import_structure(self):
        """Test that all Martin modules can be imported correctly."""
        # Test core imports
        import martin
        assert hasattr(martin, '__version__')
        
        from martin.config import config
        assert config is not None
        
        from martin.models.paper_text import PaperText
        assert PaperText is not None
        
        from martin.paper_reviewer import PaperReviewer
        assert PaperReviewer is not None
        
        # Test that main components are available
        from martin.tools.pdf_extractor import PDFTextExtractor
        from martin.tools.real_academic_search import RealAcademicSearch
        
        print("✅ Import structure test passed")