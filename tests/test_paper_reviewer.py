"""
Tests for main PaperReviewer orchestration module.

Tests the PaperReviewer DSPy module that orchestrates the complete analysis pipeline.
"""

from unittest.mock import MagicMock, Mock, patch

import dspy
import pytest

from martin.models.paper_text import PaperText
from martin.paper_reviewer import PaperReviewer


class TestPaperReviewerInitialization:
    """Test cases for PaperReviewer initialization."""

    def test_paper_reviewer_initialization_defaults(self):
        """Test PaperReviewer initialization with default settings."""
        with patch.object(PaperReviewer, "_initialize_signatures"):
            reviewer = PaperReviewer()

            assert reviewer.max_search_results == 5
            assert reviewer.enable_social_media is True
            assert reviewer.continue_on_error is False

    def test_paper_reviewer_initialization_custom_settings(self):
        """Test PaperReviewer initialization with custom settings."""
        with patch.object(PaperReviewer, "_initialize_signatures"):
            reviewer = PaperReviewer(
                max_search_results=10, enable_social_media=False, continue_on_error=True
            )

            assert reviewer.max_search_results == 10
            assert reviewer.enable_social_media is False
            assert reviewer.continue_on_error is True

    @patch("martin.paper_reviewer.PDFTextExtractor")
    @patch("martin.paper_reviewer.RealAcademicSearch")
    def test_paper_reviewer_external_tools_initialization(
        self, mock_search, mock_extractor
    ):
        """Test that external tools are properly initialized."""
        with patch.object(PaperReviewer, "_initialize_signatures"):
            reviewer = PaperReviewer(max_search_results=7)

            # Verify external tools are created
            mock_extractor.assert_called_once()
            mock_search.assert_called_once_with(max_results=7)

            assert reviewer.pdf_extractor is not None
            assert reviewer.search_engine is not None

    @patch("dspy.Predict")
    @patch("dspy.ChainOfThought")
    def test_paper_reviewer_signatures_initialization(self, mock_cot, mock_predict):
        """Test that DSPy signatures are properly initialized."""
        # Mock signature instances
        mock_predict_instance = Mock()
        mock_cot_instance = Mock()
        mock_predict.return_value = mock_predict_instance
        mock_cot.return_value = mock_cot_instance

        reviewer = PaperReviewer()

        # Verify signatures are initialized
        assert reviewer.extraction is not None
        assert reviewer.methodology is not None
        assert reviewer.contribution is not None
        assert reviewer.query_generator is not None
        assert reviewer.comparison is not None
        assert reviewer.impact is not None
        assert reviewer.verdict is not None
        assert reviewer.socials is not None


class TestPaperReviewerPipelineExecution:
    """Test cases for the main pipeline execution."""

    @patch.object(PaperReviewer, "_extract_pdf_content")
    @patch.object(PaperReviewer, "_perform_initial_extraction")
    @patch.object(PaperReviewer, "_analyze_methodology")
    @patch.object(PaperReviewer, "_analyze_contributions")
    @patch.object(PaperReviewer, "_perform_literature_comparison")
    @patch.object(PaperReviewer, "_assess_impact")
    @patch.object(PaperReviewer, "_generate_final_verdict")
    @patch.object(PaperReviewer, "_generate_social_content")
    def test_forward_complete_pipeline_success(
        self,
        mock_social,
        mock_verdict,
        mock_impact,
        mock_literature,
        mock_contributions,
        mock_methodology,
        mock_extraction,
        mock_pdf,
    ):
        """Test successful execution of complete pipeline."""
        # Setup mocks for successful execution
        mock_paper_text = Mock(spec=PaperText)
        mock_pdf.return_value = mock_paper_text

        mock_extraction_result = Mock()
        mock_extraction.return_value = mock_extraction_result

        mock_methodology_result = Mock()
        mock_methodology.return_value = mock_methodology_result

        mock_contribution_result = Mock()
        mock_contributions.return_value = mock_contribution_result

        mock_literature_result = Mock()
        mock_literature.return_value = mock_literature_result

        mock_impact_result = Mock()
        mock_impact.return_value = mock_impact_result

        mock_verdict_result = Mock()
        mock_verdict.return_value = mock_verdict_result

        with patch.object(PaperReviewer, "_initialize_signatures"):
            reviewer = PaperReviewer(enable_social_media=True)
            result = reviewer.forward("https://example.com/paper.pdf")

        # Verify all steps were called (don't check exact parameters since result is internal dict)
        mock_pdf.assert_called_once()
        mock_extraction.assert_called_once()
        mock_methodology.assert_called_once()
        mock_contributions.assert_called_once()
        mock_literature.assert_called_once()
        mock_impact.assert_called_once()
        mock_verdict.assert_called_once()
        mock_social.assert_called_once()

        # Verify result structure
        assert isinstance(result, dspy.Prediction)
        assert result.pdf_url == "https://example.com/paper.pdf"
        assert result.success is True
        assert result.errors == []
        assert result.warnings == []

    @patch.object(PaperReviewer, "_extract_pdf_content")
    def test_forward_pdf_extraction_failure(self, mock_pdf):
        """Test pipeline execution when PDF extraction fails."""
        mock_pdf.return_value = None  # PDF extraction failed

        with patch.object(PaperReviewer, "_initialize_signatures"):
            reviewer = PaperReviewer()
            result = reviewer.forward("https://example.com/paper.pdf")

        # Should return early when PDF extraction fails
        assert isinstance(result, dspy.Prediction)
        assert result.pdf_url == "https://example.com/paper.pdf"
        # Success status depends on continue_on_error setting

    @patch.object(PaperReviewer, "_extract_pdf_content")
    @patch.object(PaperReviewer, "_perform_initial_extraction")
    def test_forward_with_step_failure_continue_on_error(
        self, mock_extraction, mock_pdf
    ):
        """Test pipeline execution with step failure and continue_on_error=True."""
        mock_paper_text = Mock(spec=PaperText)
        mock_pdf.return_value = mock_paper_text

        # Mock extraction failure
        mock_extraction.side_effect = Exception("Extraction failed")

        with patch.object(PaperReviewer, "_initialize_signatures"):
            reviewer = PaperReviewer(continue_on_error=True)
            result = reviewer.forward("https://example.com/paper.pdf")

        # Should continue despite error but mark as failed
        assert isinstance(result, dspy.Prediction)
        assert result.success is False  # Should be False when critical error occurs
        assert len(result.errors) > 0  # Should record the error
        assert "I ran into a critical issue during analysis" in result.errors[0]

    @patch.object(PaperReviewer, "_extract_pdf_content")
    @patch.object(PaperReviewer, "_perform_initial_extraction")
    def test_forward_with_step_failure_no_continue(self, mock_extraction, mock_pdf):
        """Test pipeline execution with step failure and continue_on_error=False."""
        mock_paper_text = Mock(spec=PaperText)
        mock_pdf.return_value = mock_paper_text

        # Mock extraction failure
        mock_extraction.side_effect = Exception("Extraction failed")

        with patch.object(PaperReviewer, "_initialize_signatures"):
            reviewer = PaperReviewer(continue_on_error=False)

            with pytest.raises(Exception) as exc_info:
                reviewer.forward("https://example.com/paper.pdf")

            assert "Extraction failed" in str(exc_info.value)

    @patch.object(PaperReviewer, "_extract_pdf_content")
    @patch.object(PaperReviewer, "_perform_initial_extraction")
    @patch.object(PaperReviewer, "_analyze_methodology")
    @patch.object(PaperReviewer, "_analyze_contributions")
    @patch.object(PaperReviewer, "_perform_literature_comparison")
    @patch.object(PaperReviewer, "_assess_impact")
    @patch.object(PaperReviewer, "_generate_final_verdict")
    def test_forward_social_media_disabled(
        self,
        mock_verdict,
        mock_impact,
        mock_literature,
        mock_contributions,
        mock_methodology,
        mock_extraction,
        mock_pdf,
    ):
        """Test pipeline execution with social media disabled."""
        # Setup successful mocks
        mock_paper_text = Mock(spec=PaperText)
        mock_pdf.return_value = mock_paper_text
        mock_extraction.return_value = Mock()
        mock_methodology.return_value = Mock()
        mock_contributions.return_value = Mock()
        mock_literature.return_value = Mock()
        mock_impact.return_value = Mock()
        mock_verdict.return_value = Mock()

        with patch.object(PaperReviewer, "_initialize_signatures"):
            with patch.object(PaperReviewer, "_generate_social_content") as mock_social:
                reviewer = PaperReviewer(enable_social_media=False)
                result = reviewer.forward("https://example.com/paper.pdf")

                # Social media generation should not be called
                mock_social.assert_not_called()

        assert result.success is True


class TestPaperReviewerPDFExtraction:
    """Test cases for PDF extraction step."""

    @patch("martin.paper_reviewer.PDFTextExtractor")
    def test_extract_pdf_content_success(self, mock_extractor_class):
        """Test successful PDF content extraction."""
        # Mock extractor instance and result
        mock_extractor = Mock()
        mock_extractor_class.return_value = mock_extractor

        mock_paper_text = Mock(spec=PaperText)
        mock_paper_text.full_text = "Sample paper content"
        mock_paper_text.get_section_summary.return_value = {
            "abstract": True,
            "introduction": True,
        }
        mock_extractor.extract_from_url.return_value = mock_paper_text

        with patch.object(PaperReviewer, "_initialize_signatures"):
            reviewer = PaperReviewer()
            results = {"errors": [], "warnings": []}

            paper_text = reviewer._extract_pdf_content(
                "https://example.com/paper.pdf", results
            )

        assert paper_text == mock_paper_text
        assert "paper_text" in results
        assert results["paper_text"]["full_text_length"] == len("Sample paper content")
        assert results["paper_text"]["sections_found"] == {
            "abstract": True,
            "introduction": True,
        }

        mock_extractor.extract_from_url.assert_called_once_with(
            "https://example.com/paper.pdf"
        )

    @patch("martin.paper_reviewer.PDFTextExtractor")
    def test_extract_pdf_content_failure(self, mock_extractor_class):
        """Test PDF content extraction failure."""
        mock_extractor = Mock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.extract_from_url.side_effect = Exception("PDF extraction failed")

        with patch.object(PaperReviewer, "_initialize_signatures"):
            reviewer = PaperReviewer(continue_on_error=True)
            results = {"errors": [], "warnings": []}

            paper_text = reviewer._extract_pdf_content(
                "https://example.com/paper.pdf", results
            )

        assert paper_text is None
        assert len(results["errors"]) == 1
        assert "PDF extraction failed" in results["errors"][0]

    @patch("martin.paper_reviewer.PDFTextExtractor")
    def test_extract_pdf_content_failure_no_continue(self, mock_extractor_class):
        """Test PDF content extraction failure without continue_on_error."""
        mock_extractor = Mock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.extract_from_url.side_effect = Exception("PDF extraction failed")

        with patch.object(PaperReviewer, "_initialize_signatures"):
            reviewer = PaperReviewer(continue_on_error=False)
            results = {"errors": [], "warnings": []}

            with pytest.raises(Exception):
                reviewer._extract_pdf_content("https://example.com/paper.pdf", results)


class TestPaperReviewerInitialExtraction:
    """Test cases for initial extraction step."""

    def test_perform_initial_extraction_success(self):
        """Test successful initial extraction."""
        # Mock DSPy signature
        mock_extraction = Mock()
        mock_result = Mock()
        mock_result.title = "Test Paper"
        mock_result.authors = ["Author 1", "Author 2"]
        mock_result.keywords = ["keyword1", "keyword2"]
        mock_result.abstract = "Test abstract"
        mock_extraction.return_value = mock_result

        with patch.object(PaperReviewer, "_initialize_signatures"):
            reviewer = PaperReviewer()
            reviewer.extraction = mock_extraction

            mock_paper_text = Mock(spec=PaperText)
            mock_paper_text.full_text = "Sample paper text"
            results = {"errors": [], "warnings": []}

            result = reviewer._perform_initial_extraction(mock_paper_text, results)

        assert result == mock_result
        assert "extraction" in results
        assert results["extraction"]["title"] == "Test Paper"
        assert results["extraction"]["authors"] == ["Author 1", "Author 2"]
        assert results["extraction"]["keywords"] == ["keyword1", "keyword2"]
        assert results["extraction"]["abstract"] == "Test abstract"
        assert results["extraction"]["abstract_length"] == len("Test abstract")

        mock_extraction.assert_called_once_with(paper_text="Sample paper text")

    def test_perform_initial_extraction_failure(self):
        """Test initial extraction failure."""
        mock_extraction = Mock()
        mock_extraction.side_effect = Exception("Extraction failed")

        with patch.object(PaperReviewer, "_initialize_signatures"):
            reviewer = PaperReviewer(continue_on_error=True)
            reviewer.extraction = mock_extraction

            mock_paper_text = Mock(spec=PaperText)
            results = {"errors": [], "warnings": []}

            result = reviewer._perform_initial_extraction(mock_paper_text, results)

        assert result is None
        assert len(results["errors"]) == 1
        assert "I struggled with the initial paper analysis" in results["errors"][0]


class TestPaperReviewerMethodologyAnalysis:
    """Test cases for methodology analysis step."""

    def test_analyze_methodology_success(self):
        """Test successful methodology analysis."""
        mock_methodology = Mock()
        mock_result = Mock()
        mock_result.methodological_strengths = ["Strength 1", "Strength 2"]
        mock_result.methodological_weaknesses = ["Weakness 1"]
        mock_result.reproducibility_assessment = {"score": 8, "justification": "Good"}
        mock_methodology.return_value = mock_result

        with patch.object(PaperReviewer, "_initialize_signatures"):
            reviewer = PaperReviewer()
            reviewer.methodology = mock_methodology

            mock_paper_text = Mock(spec=PaperText)
            mock_paper_text.methodology = "Sample methodology content"
            results = {"errors": [], "warnings": []}

            result = reviewer._analyze_methodology(mock_paper_text, results)

        assert result == mock_result
        assert "methodology" in results
        assert results["methodology"]["methodological_strengths"] == [
            "Strength 1",
            "Strength 2",
        ]
        assert results["methodology"]["methodological_weaknesses"] == ["Weakness 1"]
        assert results["methodology"]["reproducibility_assessment"] == {
            "score": 8,
            "justification": "Good",
        }
        assert results["methodology"]["strengths_count"] == 2
        assert results["methodology"]["weaknesses_count"] == 1
        assert results["methodology"]["reproducibility_score"] == 8

        mock_methodology.assert_called_once_with(
            methodology_section="Sample methodology content"
        )

    def test_analyze_methodology_no_section(self):
        """Test methodology analysis when no methodology section is found."""
        with patch.object(PaperReviewer, "_initialize_signatures"):
            reviewer = PaperReviewer()

            mock_paper_text = Mock(spec=PaperText)
            mock_paper_text.methodology = ""  # No methodology section
            results = {"errors": [], "warnings": []}

            result = reviewer._analyze_methodology(mock_paper_text, results)

        assert result is None
        assert len(results["warnings"]) == 1
        assert "No methodology section found" in results["warnings"][0]

    def test_analyze_methodology_failure(self):
        """Test methodology analysis failure."""
        mock_methodology = Mock()
        mock_methodology.side_effect = Exception("Methodology analysis failed")

        with patch.object(PaperReviewer, "_initialize_signatures"):
            reviewer = PaperReviewer(continue_on_error=True)
            reviewer.methodology = mock_methodology

            mock_paper_text = Mock(spec=PaperText)
            mock_paper_text.methodology = "Sample methodology"
            results = {"errors": [], "warnings": []}

            result = reviewer._analyze_methodology(mock_paper_text, results)

        assert result is None
        assert len(results["errors"]) == 1
        assert "Methodology analysis failed" in results["errors"][0]


class TestPaperReviewerContributionAnalysis:
    """Test cases for contribution analysis step."""

    def test_analyze_contributions_success(self):
        """Test successful contribution analysis."""
        mock_contribution = Mock()
        mock_result = Mock()
        mock_result.claimed_contributions = ["Contribution 1", "Contribution 2"]
        mock_result.novelty_assessment = {"Contribution 1": {"novelty_score": 8}}
        mock_contribution.return_value = mock_result

        with patch.object(PaperReviewer, "_initialize_signatures"):
            reviewer = PaperReviewer()
            reviewer.contribution = mock_contribution

            mock_paper_text = Mock(spec=PaperText)
            mock_paper_text.introduction = "Sample introduction"
            mock_paper_text.conclusion = "Sample conclusion"
            results = {"errors": [], "warnings": []}

            result = reviewer._analyze_contributions(mock_paper_text, results)

        assert result == mock_result
        assert "contributions" in results
        assert results["contributions"]["claimed_contributions"] == [
            "Contribution 1",
            "Contribution 2",
        ]
        assert results["contributions"]["novelty_assessment"] == {
            "Contribution 1": {"novelty_score": 8}
        }
        assert results["contributions"]["claimed_contributions_count"] == 2
        assert results["contributions"]["novelty_assessments"] == 1

        mock_contribution.assert_called_once_with(
            introduction="Sample introduction", conclusion="Sample conclusion"
        )

    def test_analyze_contributions_missing_sections(self):
        """Test contribution analysis with missing introduction or conclusion."""
        mock_contribution = Mock()
        mock_result = Mock()
        mock_result.claimed_contributions = ["Contribution 1"]
        mock_result.novelty_assessment = {}
        mock_contribution.return_value = mock_result

        with patch.object(PaperReviewer, "_initialize_signatures"):
            reviewer = PaperReviewer()
            reviewer.contribution = mock_contribution

            mock_paper_text = Mock(spec=PaperText)
            mock_paper_text.introduction = ""  # Missing introduction
            mock_paper_text.conclusion = "Sample conclusion"
            mock_paper_text.abstract = "Sample abstract"
            results = {"errors": [], "warnings": []}

            result = reviewer._analyze_contributions(mock_paper_text, results)

        assert result == mock_result
        assert len(results["warnings"]) == 1
        assert "Missing introduction or conclusion sections" in results["warnings"][0]

        # Should use abstract as fallback for missing introduction
        mock_contribution.assert_called_once_with(
            introduction="Sample abstract", conclusion="Sample conclusion"
        )

    def test_analyze_contributions_failure(self):
        """Test contribution analysis failure."""
        mock_contribution = Mock()
        mock_contribution.side_effect = Exception("Contribution analysis failed")

        with patch.object(PaperReviewer, "_initialize_signatures"):
            reviewer = PaperReviewer(continue_on_error=True)
            reviewer.contribution = mock_contribution

            mock_paper_text = Mock(spec=PaperText)
            mock_paper_text.introduction = "Sample introduction"
            mock_paper_text.conclusion = "Sample conclusion"
            results = {"errors": [], "warnings": []}

            result = reviewer._analyze_contributions(mock_paper_text, results)

        assert result is None
        assert len(results["errors"]) == 1
        assert "Contribution analysis failed" in results["errors"][0]


class TestPaperReviewerLiteratureComparison:
    """Test cases for literature comparison step."""

    @patch("martin.paper_reviewer.RealAcademicSearch")
    def test_perform_literature_comparison_success(self, mock_search_class):
        """Test successful literature comparison."""
        # Mock search engine
        mock_search_engine = Mock()
        mock_search_class.return_value = mock_search_engine

        # Mock search results
        mock_search_result = Mock()
        mock_search_result.title = "Related Paper"
        mock_search_result.authors = ["Author 1"]
        mock_search_result.abstract = "Related abstract"
        mock_search_result.year = 2020
        mock_search_result.venue = "Conference"
        mock_search_result.citation_count = 100
        mock_search_result.relevance_score = 0.8
        mock_search_engine.search.return_value = [mock_search_result]

        # Mock DSPy signatures
        mock_query_generator = Mock()
        mock_query_result = Mock()
        mock_query_result.search_queries = ["query1", "query2"]
        mock_query_generator.return_value = mock_query_result

        mock_comparison = Mock()
        mock_comparison_result = Mock()
        mock_comparison_result.context = "Research context"
        mock_comparison_result.differentiation = "Key differences"
        mock_comparison_result.standing_in_field = "Field standing"
        mock_comparison.return_value = mock_comparison_result

        with patch.object(PaperReviewer, "_initialize_signatures"):
            reviewer = PaperReviewer()
            reviewer.search_engine = mock_search_engine
            reviewer.query_generator = mock_query_generator
            reviewer.comparison = mock_comparison

            mock_extraction_result = Mock()
            mock_extraction_result.title = "Test Paper"
            mock_extraction_result.abstract = "Test abstract"

            mock_contribution_result = Mock()
            mock_contribution_result.claimed_contributions = ["Contribution 1"]

            results = {"errors": [], "warnings": []}

            result = reviewer._perform_literature_comparison(
                mock_extraction_result, mock_contribution_result, results
            )

        assert result == mock_comparison_result
        assert "literature" in results
        assert results["literature"]["context"] == "Research context"
        assert results["literature"]["differentiation"] == "Key differences"
        assert results["literature"]["standing_in_field"] == "Field standing"
        assert results["literature"]["search_queries"] == ["query1", "query2"]
        assert len(results["literature"]["search_results"]) == 1
        assert results["literature"]["papers_found"] == 1
        assert results["literature"]["comparison_completed"] is True

    def test_perform_literature_comparison_no_extraction(self):
        """Test literature comparison when extraction result is missing."""
        with patch.object(PaperReviewer, "_initialize_signatures"):
            reviewer = PaperReviewer()

            results = {"errors": [], "warnings": []}

            result = reviewer._perform_literature_comparison(None, Mock(), results)

        assert result is None
        assert len(results["warnings"]) == 1
        assert (
            "Skipping literature comparison - no extraction results"
            in results["warnings"][0]
        )

    @patch("martin.paper_reviewer.RealAcademicSearch")
    def test_perform_literature_comparison_search_failure(self, mock_search_class):
        """Test literature comparison with search failures."""
        mock_search_engine = Mock()
        mock_search_class.return_value = mock_search_engine
        mock_search_engine.search.side_effect = Exception("Search failed")

        mock_query_generator = Mock()
        mock_query_result = Mock()
        mock_query_result.search_queries = ["query1"]
        mock_query_generator.return_value = mock_query_result

        with patch.object(PaperReviewer, "_initialize_signatures"):
            reviewer = PaperReviewer()
            reviewer.search_engine = mock_search_engine
            reviewer.query_generator = mock_query_generator

            mock_extraction_result = Mock()
            mock_extraction_result.title = "Test Paper"
            mock_extraction_result.abstract = "Test abstract"

            mock_contribution_result = Mock()
            mock_contribution_result.claimed_contributions = ["Contribution 1"]

            results = {"errors": [], "warnings": []}

            result = reviewer._perform_literature_comparison(
                mock_extraction_result, mock_contribution_result, results
            )

        assert result is None
        assert len(results["warnings"]) == 2  # Search failure + No literature found
        assert "Had trouble with one search query 'query1'" in results["warnings"][0]
        assert "No literature found for comparison" in results["warnings"][1]


class TestPaperReviewerImpactAssessment:
    """Test cases for impact assessment step."""

    def test_assess_impact_success(self):
        """Test successful impact assessment."""
        mock_impact = Mock()
        mock_result = Mock()
        mock_result.field_impact = {"impact_score": 8, "reasoning": "High impact"}
        mock_result.societal_impact = {
            "impact_score": 6,
            "reasoning": "Moderate impact",
        }
        mock_impact.return_value = mock_result

        with patch.object(PaperReviewer, "_initialize_signatures"):
            reviewer = PaperReviewer()
            reviewer.impact = mock_impact

            mock_methodology_result = Mock()
            mock_methodology_result.methodological_strengths = ["Strength 1"]
            mock_methodology_result.methodological_weaknesses = ["Weakness 1"]
            mock_methodology_result.reproducibility_assessment = {"score": 8}

            mock_contribution_result = Mock()
            mock_contribution_result.claimed_contributions = ["Contribution 1"]
            mock_contribution_result.novelty_assessment = {"assessment": "novel"}

            mock_literature_result = Mock()
            mock_literature_result.context = "Context"
            mock_literature_result.differentiation = "Differentiation"
            mock_literature_result.standing_in_field = "Standing"

            results = {"errors": [], "warnings": []}

            result = reviewer._assess_impact(
                mock_methodology_result,
                mock_contribution_result,
                mock_literature_result,
                results,
            )

        assert result == mock_result
        assert "impact" in results
        assert results["impact"]["field_impact"] == {
            "impact_score": 8,
            "reasoning": "High impact",
        }
        assert results["impact"]["societal_impact"] == {
            "impact_score": 6,
            "reasoning": "Moderate impact",
        }
        assert results["impact"]["field_impact_score"] == 8
        assert results["impact"]["societal_impact_score"] == 6

    def test_assess_impact_insufficient_data(self):
        """Test impact assessment with insufficient data."""
        with patch.object(PaperReviewer, "_initialize_signatures"):
            reviewer = PaperReviewer()

            results = {"errors": [], "warnings": []}

            result = reviewer._assess_impact(None, None, None, results)

        assert result is None
        assert len(results["warnings"]) == 1
        assert "Insufficient data for impact assessment" in results["warnings"][0]


class TestPaperReviewerFinalVerdict:
    """Test cases for final verdict generation."""

    def test_generate_final_verdict_success(self):
        """Test successful final verdict generation."""
        mock_verdict = Mock()
        mock_result = Mock()
        mock_result.recommendation = "Highly Recommended"
        mock_result.justification = "Excellent work"
        mock_result.worth_reading_verdict = True
        mock_result.key_takeaways = ["Takeaway 1", "Takeaway 2"]
        mock_verdict.return_value = mock_result

        with patch.object(PaperReviewer, "_initialize_signatures"):
            reviewer = PaperReviewer()
            reviewer.verdict = mock_verdict

            # Mock all input results
            mock_extraction_result = Mock()
            mock_extraction_result.title = "Test Paper"
            mock_extraction_result.authors = ["Author 1"]
            mock_extraction_result.keywords = ["keyword1"]

            mock_methodology_result = Mock()
            mock_methodology_result.methodological_strengths = ["Strength 1"]
            mock_methodology_result.methodological_weaknesses = ["Weakness 1"]
            mock_methodology_result.reproducibility_assessment = {"score": 8}

            mock_contribution_result = Mock()
            mock_contribution_result.claimed_contributions = ["Contribution 1"]
            mock_contribution_result.novelty_assessment = {"assessment": "novel"}

            mock_literature_result = Mock()
            mock_literature_result.context = "Context"
            mock_literature_result.differentiation = "Differentiation"
            mock_literature_result.standing_in_field = "Standing"

            mock_impact_result = Mock()
            mock_impact_result.field_impact = {"impact_score": 8}
            mock_impact_result.societal_impact = {"impact_score": 6}

            results = {"errors": [], "warnings": []}

            result = reviewer._generate_final_verdict(
                mock_extraction_result,
                mock_methodology_result,
                mock_contribution_result,
                mock_literature_result,
                mock_impact_result,
                results,
            )

        assert result == mock_result
        assert "verdict" in results
        assert results["verdict"]["recommendation"] == "Highly Recommended"
        assert results["verdict"]["justification"] == "Excellent work"
        assert results["verdict"]["worth_reading"] is True
        assert results["verdict"]["key_takeaways"] == ["Takeaway 1", "Takeaway 2"]
        assert results["verdict"]["key_takeaways_count"] == 2

    def test_generate_final_verdict_insufficient_data(self):
        """Test final verdict generation with insufficient data."""
        with patch.object(PaperReviewer, "_initialize_signatures"):
            reviewer = PaperReviewer()

            results = {"errors": [], "warnings": []}

            result = reviewer._generate_final_verdict(
                None, None, None, None, None, results
            )

        assert result is None
        assert len(results["warnings"]) == 1
        assert "Insufficient data for final verdict" in results["warnings"][0]


class TestPaperReviewerSocialMediaGeneration:
    """Test cases for social media content generation."""

    def test_generate_social_content_success(self):
        """Test successful social media content generation."""
        mock_socials = Mock()
        mock_result = Mock()
        mock_result.twitter_thread = ["Tweet 1", "Tweet 2"]
        mock_result.linkedin_post = "LinkedIn post content"
        mock_socials.return_value = mock_result

        with patch.object(PaperReviewer, "_initialize_signatures"):
            reviewer = PaperReviewer()
            reviewer.socials = mock_socials

            mock_extraction_result = Mock()
            mock_extraction_result.title = "Test Paper"

            mock_verdict_result = Mock()
            mock_verdict_result.recommendation = "Highly Recommended"
            mock_verdict_result.key_takeaways = ["Takeaway 1"]

            mock_impact_result = Mock()
            mock_impact_result.field_impact = {"impact_score": 8}

            results = {"errors": [], "warnings": []}

            reviewer._generate_social_content(
                mock_extraction_result, mock_verdict_result, mock_impact_result, results
            )

        assert "social_media" in results
        assert results["social_media"]["generated"] is True
        assert results["social_media"]["twitter_thread"] == ["Tweet 1", "Tweet 2"]
        assert results["social_media"]["linkedin_post"] == "LinkedIn post content"
        assert results["social_media"]["twitter_thread_length"] == 2
        assert results["social_media"]["linkedin_post_length"] == len(
            "LinkedIn post content"
        )

    def test_generate_social_content_not_recommended(self):
        """Test social media generation for non-recommended papers."""
        with patch.object(PaperReviewer, "_initialize_signatures"):
            reviewer = PaperReviewer()

            mock_extraction_result = Mock()
            mock_verdict_result = Mock()
            mock_verdict_result.recommendation = "Should be Ignored"  # Not recommended
            mock_impact_result = Mock()

            results = {"errors": [], "warnings": []}

            reviewer._generate_social_content(
                mock_extraction_result, mock_verdict_result, mock_impact_result, results
            )

        assert "social_media" in results
        assert results["social_media"]["generated"] is False
        assert (
            results["social_media"]["reason"] == "Paper not recommended for promotion"
        )

    def test_generate_social_content_insufficient_data(self):
        """Test social media generation with insufficient data."""
        with patch.object(PaperReviewer, "_initialize_signatures"):
            reviewer = PaperReviewer()

            mock_verdict_result = Mock()
            mock_verdict_result.recommendation = "Highly Recommended"

            results = {"errors": [], "warnings": []}

            reviewer._generate_social_content(None, mock_verdict_result, None, results)

        assert len(results["warnings"]) == 1
        assert "Insufficient data for social media generation" in results["warnings"][0]


class TestPaperReviewerConvenienceMethod:
    """Test cases for the convenience review method."""

    def test_review_method(self):
        """Test that review method calls forward."""
        with patch.object(PaperReviewer, "_initialize_signatures"):
            with patch.object(PaperReviewer, "forward") as mock_forward:
                mock_result = Mock()
                mock_forward.return_value = mock_result

                reviewer = PaperReviewer()
                result = reviewer.review("https://example.com/paper.pdf")

        assert result == mock_result
        mock_forward.assert_called_once_with("https://example.com/paper.pdf")


class TestPaperReviewerErrorHandling:
    """Test cases for error handling throughout the pipeline."""

    def test_critical_pipeline_error_continue_on_error(self):
        """Test critical pipeline error with continue_on_error=True."""
        with patch.object(PaperReviewer, "_initialize_signatures"):
            with patch.object(PaperReviewer, "_extract_pdf_content") as mock_pdf:
                mock_pdf.side_effect = Exception("Critical error")

                reviewer = PaperReviewer(continue_on_error=True)
                result = reviewer.forward("https://example.com/paper.pdf")

        assert isinstance(result, dspy.Prediction)
        assert result.success is False
        assert len(result.errors) == 1
        assert "I ran into a critical issue during analysis" in result.errors[0]

    def test_critical_pipeline_error_no_continue(self):
        """Test critical pipeline error with continue_on_error=False."""
        with patch.object(PaperReviewer, "_initialize_signatures"):
            with patch.object(PaperReviewer, "_extract_pdf_content") as mock_pdf:
                mock_pdf.side_effect = Exception("Critical error")

                reviewer = PaperReviewer(continue_on_error=False)

                with pytest.raises(Exception) as exc_info:
                    reviewer.forward("https://example.com/paper.pdf")

                assert "Critical error" in str(exc_info.value)
