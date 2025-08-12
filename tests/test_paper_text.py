"""
Tests for PaperText Pydantic model.

Tests model validation, utility methods, and edge cases for the PaperText data model.
"""

import pytest
from pydantic import ValidationError

from martin.models.paper_text import PaperText
from tests.fixtures.sample_papers import get_sample_paper, get_sample_sections


class TestPaperTextModel:
    """Test cases for PaperText Pydantic model."""

    def test_model_creation_with_valid_data(self):
        """Test PaperText model creation with valid data."""
        paper_data = get_sample_paper("transformer")

        paper_text = PaperText(
            full_text=paper_data["full_text"],
            abstract=paper_data["sections"]["abstract"],
            introduction=paper_data["sections"]["introduction"],
            methodology=paper_data["sections"]["methodology"],
            results=paper_data["sections"]["results"],
            conclusion=paper_data["sections"]["conclusion"],
            references=paper_data["sections"]["references"],
        )

        assert paper_text.full_text == paper_data["full_text"]
        assert paper_text.abstract == paper_data["sections"]["abstract"]
        assert paper_text.introduction == paper_data["sections"]["introduction"]
        assert paper_text.methodology == paper_data["sections"]["methodology"]
        assert paper_text.results == paper_data["sections"]["results"]
        assert paper_text.conclusion == paper_data["sections"]["conclusion"]
        assert paper_text.references == paper_data["sections"]["references"]

    def test_model_creation_with_minimal_data(self):
        """Test PaperText model creation with only required fields."""
        full_text = "This is a minimal paper with just full text."

        paper_text = PaperText(full_text=full_text)

        assert paper_text.full_text == full_text
        assert paper_text.abstract == ""
        assert paper_text.introduction == ""
        assert paper_text.methodology == ""
        assert paper_text.results == ""
        assert paper_text.conclusion == ""
        assert paper_text.references == ""

    def test_model_creation_with_empty_full_text(self):
        """Test PaperText model creation with empty full text."""
        paper_text = PaperText(full_text="")

        assert paper_text.full_text == ""
        assert paper_text.abstract == ""

    def test_model_validation_missing_required_field(self):
        """Test that ValidationError is raised when required field is missing."""
        with pytest.raises(ValidationError) as exc_info:
            PaperText()  # Missing required full_text field

        error = exc_info.value
        assert "full_text" in str(error)
        assert "Field required" in str(error)

    def test_model_validation_wrong_field_types(self):
        """Test that ValidationError is raised for wrong field types."""
        with pytest.raises(ValidationError) as exc_info:
            PaperText(
                full_text=123,  # Should be string
                abstract=["not", "a", "string"],  # Should be string
            )

        error = exc_info.value
        assert "Input should be a valid string" in str(error)

    def test_has_section_method(self):
        """Test has_section method with various section states."""
        paper_data = get_sample_paper("transformer")
        paper_text = PaperText(
            full_text=paper_data["full_text"],
            abstract=paper_data["sections"]["abstract"],
            introduction=paper_data["sections"]["introduction"],
            methodology="",  # Empty section
            results=paper_data["sections"]["results"],
            conclusion="   ",  # Whitespace only
            references=paper_data["sections"]["references"],
        )

        # Test sections with content
        assert paper_text.has_section("abstract") is True
        assert paper_text.has_section("introduction") is True
        assert paper_text.has_section("results") is True
        assert paper_text.has_section("references") is True

        # Test empty sections
        assert paper_text.has_section("methodology") is False
        assert paper_text.has_section("conclusion") is False

        # Test non-existent section
        assert paper_text.has_section("nonexistent") is False

    def test_has_section_with_none_values(self):
        """Test has_section method handles None values gracefully."""
        paper_text = PaperText(full_text="test")

        # Manually set a field to None (shouldn't happen in normal usage)
        paper_text.abstract = None

        # Should handle None gracefully
        assert paper_text.has_section("abstract") is False

    def test_get_section_summary_method(self):
        """Test get_section_summary method returns correct availability."""
        paper_data = get_sample_paper("minimal")
        paper_text = PaperText(
            full_text=paper_data["full_text"],
            abstract=paper_data["sections"]["abstract"],
            introduction="",  # Empty
            methodology="",  # Empty
            results="",  # Empty
            conclusion=paper_data["sections"]["conclusion"],
            references="",  # Empty
        )

        summary = paper_text.get_section_summary()

        expected_summary = {
            "abstract": True,
            "introduction": False,
            "methodology": False,
            "results": False,
            "conclusion": True,
            "references": False,
        }

        assert summary == expected_summary
        assert isinstance(summary, dict)
        assert len(summary) == 6

    def test_get_section_summary_all_empty(self):
        """Test get_section_summary with all sections empty."""
        paper_text = PaperText(full_text="Just full text, no sections")

        summary = paper_text.get_section_summary()

        expected_summary = {
            "abstract": False,
            "introduction": False,
            "methodology": False,
            "results": False,
            "conclusion": False,
            "references": False,
        }

        assert summary == expected_summary

    def test_get_section_summary_all_present(self):
        """Test get_section_summary with all sections present."""
        paper_data = get_sample_paper("transformer")
        paper_text = PaperText(
            full_text=paper_data["full_text"], **paper_data["sections"]
        )

        summary = paper_text.get_section_summary()

        # All sections should be True for transformer paper
        assert all(summary.values())
        assert len(summary) == 6

    def test_get_main_content_method(self):
        """Test get_main_content method combines sections correctly."""
        paper_text = PaperText(
            full_text="Full text content",
            abstract="Test abstract",
            introduction="Test introduction",
            methodology="Test methodology",
            results="Test results",
            conclusion="Test conclusion",
            references="Test references",
        )

        main_content = paper_text.get_main_content()

        # Should include all main sections with headers
        assert "Abstract:\nTest abstract" in main_content
        assert "Introduction:\nTest introduction" in main_content
        assert "Methodology:\nTest methodology" in main_content
        assert "Results:\nTest results" in main_content
        assert "Conclusion:\nTest conclusion" in main_content

        # Should not include references in main content
        assert "References:" not in main_content
        assert "Test references" not in main_content

        # Should be properly formatted with double newlines
        sections = main_content.split("\n\n")
        assert len(sections) >= 5  # At least 5 main sections

    def test_get_main_content_with_empty_sections(self):
        """Test get_main_content method with some empty sections."""
        paper_text = PaperText(
            full_text="Full text content",
            abstract="Test abstract",
            introduction="",  # Empty
            methodology="Test methodology",
            results="",  # Empty
            conclusion="Test conclusion",
            references="Test references",
        )

        main_content = paper_text.get_main_content()

        # Should include only non-empty sections
        assert "Abstract:\nTest abstract" in main_content
        assert "Methodology:\nTest methodology" in main_content
        assert "Conclusion:\nTest conclusion" in main_content

        # Should not include empty sections
        assert "Introduction:" not in main_content
        assert "Results:" not in main_content
        assert "References:" not in main_content

    def test_get_main_content_all_sections_empty(self):
        """Test get_main_content method when all sections are empty."""
        full_text = "This is the full text content"
        paper_text = PaperText(full_text=full_text)

        main_content = paper_text.get_main_content()

        # Should return full text when no sections are available
        assert main_content == full_text

    def test_get_main_content_with_whitespace_sections(self):
        """Test get_main_content method handles whitespace-only sections."""
        paper_text = PaperText(
            full_text="Full text content",
            abstract="Test abstract",
            introduction="   ",  # Whitespace only
            methodology="Test methodology",
            results="\n\t\n",  # Whitespace only
            conclusion="Test conclusion",
            references="",
        )

        main_content = paper_text.get_main_content()

        # Should include only sections with actual content
        assert "Abstract:\nTest abstract" in main_content
        assert "Methodology:\nTest methodology" in main_content
        assert "Conclusion:\nTest conclusion" in main_content

        # Should not include whitespace-only sections
        assert "Introduction:" not in main_content
        assert "Results:" not in main_content


class TestPaperTextEdgeCases:
    """Test edge cases and error conditions for PaperText model."""

    def test_model_with_very_long_text(self):
        """Test model handles very long text content."""
        long_text = "A" * 100000  # 100k characters

        paper_text = PaperText(
            full_text=long_text, abstract="B" * 10000  # 10k characters
        )

        assert len(paper_text.full_text) == 100000
        assert len(paper_text.abstract) == 10000
        assert paper_text.has_section("abstract") is True

    def test_model_with_unicode_content(self):
        """Test model handles Unicode characters correctly."""
        unicode_text = (
            "Résumé: This paper discusses naïve approaches to AI. 中文测试 🤖"
        )

        paper_text = PaperText(
            full_text=unicode_text,
            abstract="Résumé with émojis 🧠",
            conclusion="Conclusión en español",
        )

        assert paper_text.full_text == unicode_text
        assert "émojis 🧠" in paper_text.abstract
        assert "español" in paper_text.conclusion
        assert paper_text.has_section("abstract") is True
        assert paper_text.has_section("conclusion") is True

    def test_model_with_special_characters(self):
        """Test model handles special characters and formatting."""
        special_text = """
        Title: Test Paper with Special Characters
        
        Abstract: This contains <HTML> tags, [brackets], {braces}, 
        and other special chars: @#$%^&*()_+-=[]{}|;':\",./<>?
        
        Math: ∑(x²) = ∫f(x)dx, α + β = γ
        """

        paper_text = PaperText(
            full_text=special_text, abstract="Contains <tags> and math: α + β = γ"
        )

        assert "<tags>" in paper_text.abstract
        assert "α + β = γ" in paper_text.abstract
        assert paper_text.has_section("abstract") is True

    def test_model_serialization(self):
        """Test model can be serialized and deserialized."""
        paper_data = get_sample_paper("transformer")
        original = PaperText(
            full_text=paper_data["full_text"], **paper_data["sections"]
        )

        # Test dict conversion
        paper_dict = original.model_dump()
        assert isinstance(paper_dict, dict)
        assert paper_dict["full_text"] == paper_data["full_text"]
        assert paper_dict["abstract"] == paper_data["sections"]["abstract"]

        # Test reconstruction from dict
        reconstructed = PaperText(**paper_dict)
        assert reconstructed.full_text == original.full_text
        assert reconstructed.abstract == original.abstract
        assert reconstructed.get_section_summary() == original.get_section_summary()

    def test_model_json_serialization(self):
        """Test model JSON serialization and deserialization."""
        paper_text = PaperText(full_text="Test content", abstract="Test abstract")

        # Test JSON serialization
        json_str = paper_text.model_dump_json()
        assert isinstance(json_str, str)
        assert "Test content" in json_str
        assert "Test abstract" in json_str

        # Test JSON deserialization
        reconstructed = PaperText.model_validate_json(json_str)
        assert reconstructed.full_text == paper_text.full_text
        assert reconstructed.abstract == paper_text.abstract


class TestPaperTextIntegration:
    """Integration tests for PaperText model with sample data."""

    @pytest.mark.parametrize("paper_type", ["transformer", "minimal", "incomplete"])
    def test_model_with_sample_papers(self, paper_type):
        """Test model creation with different sample paper types."""
        paper_data = get_sample_paper(paper_type)

        paper_text = PaperText(
            full_text=paper_data["full_text"], **paper_data["sections"]
        )

        assert paper_text.full_text == paper_data["full_text"]

        # Test section availability matches expectations
        summary = paper_text.get_section_summary()

        if paper_type == "transformer":
            # Transformer paper should have all sections
            assert summary["abstract"] is True
            assert summary["introduction"] is True
            assert summary["conclusion"] is True
        elif paper_type == "minimal":
            # Minimal paper should have abstract and conclusion
            assert summary["abstract"] is True
            assert summary["conclusion"] is True
        elif paper_type == "incomplete":
            # Incomplete paper should have no sections
            assert all(not available for available in summary.values())

    def test_model_with_realistic_content_lengths(self):
        """Test model with realistic academic paper content lengths."""
        # Simulate realistic paper sections
        paper_text = PaperText(
            full_text="A" * 50000,  # ~50k chars (typical paper length)
            abstract="B" * 1500,  # ~1.5k chars (typical abstract)
            introduction="C" * 5000,  # ~5k chars (typical intro)
            methodology="D" * 8000,  # ~8k chars (typical methods)
            results="E" * 6000,  # ~6k chars (typical results)
            conclusion="F" * 2000,  # ~2k chars (typical conclusion)
            references="G" * 3000,  # ~3k chars (typical references)
        )

        # Test all sections are recognized as present
        summary = paper_text.get_section_summary()
        assert all(summary.values())

        # Test main content excludes references
        main_content = paper_text.get_main_content()
        assert "References:" not in main_content
        assert len(main_content) < len(
            paper_text.full_text
        )  # Should be shorter than full text
