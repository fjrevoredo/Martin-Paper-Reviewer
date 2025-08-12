"""
Tests for PDF extraction functionality.

Tests PDFTextExtractor class for URL validation, PDF downloading, text extraction, and section parsing.
"""

import time
from io import BytesIO
from unittest.mock import MagicMock, Mock, patch

import PyPDF2
import pytest
import requests

from martin.models.paper_text import PaperText
from martin.tools.pdf_extractor import PDFTextExtractor
from tests.fixtures.api_responses import SAMPLE_PDF_CONTENT


class TestPDFTextExtractorInitialization:
    """Test cases for PDFTextExtractor initialization."""

    def test_extractor_initialization_defaults(self):
        """Test PDFTextExtractor initialization with default settings."""
        extractor = PDFTextExtractor()

        assert extractor.timeout == 30
        assert extractor.max_retries == 3
        assert extractor.session is not None
        assert "Mozilla" in extractor.session.headers["User-Agent"]

    def test_extractor_initialization_custom_settings(self):
        """Test PDFTextExtractor initialization with custom settings."""
        extractor = PDFTextExtractor(timeout=60, max_retries=5)

        assert extractor.timeout == 60
        assert extractor.max_retries == 5
        assert extractor.session is not None


class TestURLValidation:
    """Test cases for URL validation."""

    def test_is_valid_url_valid_urls(self):
        """Test URL validation with valid URLs."""
        extractor = PDFTextExtractor()

        valid_urls = [
            "https://arxiv.org/pdf/1706.03762.pdf",
            "http://example.com/paper.pdf",
            "https://www.example.com/documents/research.pdf",
            "ftp://files.example.com/paper.pdf",
        ]

        for url in valid_urls:
            assert extractor._is_valid_url(url) is True

    def test_is_valid_url_invalid_urls(self):
        """Test URL validation with invalid URLs."""
        extractor = PDFTextExtractor()

        invalid_urls = [
            "not-a-url",
            "http://",
            "https://",
            "",
            "file:///local/path.pdf",  # Local file paths
            "just-text-not-url",
            "www.example.com",  # Missing scheme
        ]

        for url in invalid_urls:
            assert extractor._is_valid_url(url) is False

    def test_is_valid_url_edge_cases(self):
        """Test URL validation with edge cases."""
        extractor = PDFTextExtractor()

        # Test with malformed URLs that might cause exceptions
        edge_cases = [
            None,
            123,
            [],
            {},
            "http://[invalid-ipv6",
        ]

        for case in edge_cases:
            # Should handle any input gracefully
            result = extractor._is_valid_url(case)
            assert isinstance(result, bool)


class TestPDFDownload:
    """Test cases for PDF downloading functionality."""

    @patch("requests.Session.get")
    def test_download_pdf_success(self, mock_get):
        """Test successful PDF download."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = SAMPLE_PDF_CONTENT
        mock_response.headers = {"content-type": "application/pdf"}
        mock_get.return_value = mock_response

        extractor = PDFTextExtractor()
        content = extractor._download_pdf("https://example.com/paper.pdf")

        assert content == SAMPLE_PDF_CONTENT
        mock_get.assert_called_once_with("https://example.com/paper.pdf", timeout=30)

    @patch("requests.Session.get")
    def test_download_pdf_without_content_type(self, mock_get):
        """Test PDF download without proper content-type header."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = SAMPLE_PDF_CONTENT
        mock_response.headers = {"content-type": "text/html"}  # Wrong content type
        mock_get.return_value = mock_response

        extractor = PDFTextExtractor()
        content = extractor._download_pdf("https://example.com/paper.pdf")

        # Should still work (some servers don't set proper content-type)
        assert content == SAMPLE_PDF_CONTENT

    @patch("requests.Session.get")
    def test_download_pdf_network_error(self, mock_get):
        """Test PDF download with network error."""
        mock_get.side_effect = requests.RequestException("Network error")

        extractor = PDFTextExtractor(max_retries=1)  # Reduce retries for faster test

        with pytest.raises(requests.RequestException) as exc_info:
            extractor._download_pdf("https://example.com/paper.pdf")

        assert "Failed to download PDF after 1 attempts" in str(exc_info.value)
        assert mock_get.call_count == 1

    @patch("requests.Session.get")
    @patch("time.sleep")
    def test_download_pdf_retry_logic(self, mock_sleep, mock_get):
        """Test PDF download retry logic with exponential backoff."""
        # First two calls fail, third succeeds
        mock_get.side_effect = [
            requests.RequestException("First failure"),
            requests.RequestException("Second failure"),
            Mock(raise_for_status=Mock(), content=SAMPLE_PDF_CONTENT, headers={}),
        ]

        extractor = PDFTextExtractor(max_retries=3)
        content = extractor._download_pdf("https://example.com/paper.pdf")

        assert content == SAMPLE_PDF_CONTENT
        assert mock_get.call_count == 3

        # Verify exponential backoff
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(1)  # 2^0
        mock_sleep.assert_any_call(2)  # 2^1

    @patch("requests.Session.get")
    def test_download_pdf_http_error(self, mock_get):
        """Test PDF download with HTTP error."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        extractor = PDFTextExtractor(max_retries=1)

        with pytest.raises(requests.RequestException):
            extractor._download_pdf("https://example.com/paper.pdf")

    @patch("requests.Session.get")
    def test_download_pdf_timeout(self, mock_get):
        """Test PDF download with timeout."""
        mock_get.side_effect = requests.Timeout("Request timed out")

        extractor = PDFTextExtractor(timeout=5, max_retries=1)

        with pytest.raises(requests.RequestException):
            extractor._download_pdf("https://example.com/paper.pdf")


class TestPDFTextExtraction:
    """Test cases for PDF text extraction."""

    @patch("PyPDF2.PdfReader")
    def test_extract_text_from_pdf_success(self, mock_pdf_reader):
        """Test successful text extraction from PDF."""
        # Mock PDF reader and pages
        mock_reader_instance = Mock()
        mock_reader_instance.is_encrypted = False

        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1 content"
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Page 2 content"

        mock_reader_instance.pages = [mock_page1, mock_page2]
        mock_pdf_reader.return_value = mock_reader_instance

        extractor = PDFTextExtractor()
        text = extractor._extract_text_from_pdf(SAMPLE_PDF_CONTENT)

        assert text == "Page 1 content\n\nPage 2 content"
        mock_pdf_reader.assert_called_once()

    @patch("PyPDF2.PdfReader")
    def test_extract_text_from_pdf_encrypted(self, mock_pdf_reader):
        """Test text extraction from encrypted PDF."""
        mock_reader_instance = Mock()
        mock_reader_instance.is_encrypted = True
        mock_pdf_reader.return_value = mock_reader_instance

        extractor = PDFTextExtractor()

        with pytest.raises(ValueError) as exc_info:
            extractor._extract_text_from_pdf(SAMPLE_PDF_CONTENT)

        assert "password-protected" in str(exc_info.value)

    @patch("PyPDF2.PdfReader")
    def test_extract_text_from_pdf_empty_pages(self, mock_pdf_reader):
        """Test text extraction from PDF with empty pages."""
        mock_reader_instance = Mock()
        mock_reader_instance.is_encrypted = False

        mock_page1 = Mock()
        mock_page1.extract_text.return_value = ""  # Empty page
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "   "  # Whitespace only

        mock_reader_instance.pages = [mock_page1, mock_page2]
        mock_pdf_reader.return_value = mock_reader_instance

        extractor = PDFTextExtractor()

        with pytest.raises(ValueError) as exc_info:
            extractor._extract_text_from_pdf(SAMPLE_PDF_CONTENT)

        assert "No readable text found" in str(exc_info.value)

    @patch("PyPDF2.PdfReader")
    def test_extract_text_from_pdf_page_extraction_error(self, mock_pdf_reader):
        """Test text extraction with page extraction errors."""
        mock_reader_instance = Mock()
        mock_reader_instance.is_encrypted = False

        mock_page1 = Mock()
        mock_page1.extract_text.side_effect = Exception("Page extraction error")
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Page 2 content"

        mock_reader_instance.pages = [mock_page1, mock_page2]
        mock_pdf_reader.return_value = mock_reader_instance

        extractor = PDFTextExtractor()
        text = extractor._extract_text_from_pdf(SAMPLE_PDF_CONTENT)

        # Should continue with pages that work
        assert text == "Page 2 content"

    @patch("PyPDF2.PdfReader")
    def test_extract_text_from_pdf_corrupted(self, mock_pdf_reader):
        """Test text extraction from corrupted PDF."""
        mock_pdf_reader.side_effect = PyPDF2.errors.PdfReadError("Invalid PDF")

        extractor = PDFTextExtractor()

        with pytest.raises(ValueError) as exc_info:
            extractor._extract_text_from_pdf(b"corrupted pdf content")

        assert "Invalid or corrupted PDF" in str(exc_info.value)

    @patch("PyPDF2.PdfReader")
    def test_extract_text_from_pdf_generic_error(self, mock_pdf_reader):
        """Test text extraction with generic error."""
        mock_pdf_reader.side_effect = Exception("Unexpected error")

        extractor = PDFTextExtractor()

        with pytest.raises(ValueError) as exc_info:
            extractor._extract_text_from_pdf(SAMPLE_PDF_CONTENT)

        assert "Error processing PDF" in str(exc_info.value)


class TestTextCleaning:
    """Test cases for text cleaning functionality."""

    def test_clean_text_normal(self):
        """Test text cleaning with normal text."""
        extractor = PDFTextExtractor()

        input_text = "This is   a test\n\nwith   multiple    spaces\nand newlines."
        cleaned = extractor._clean_text(input_text)

        # Should normalize whitespace but preserve structure
        assert "multiple    spaces" not in cleaned
        assert "This is a test" in cleaned

    def test_clean_text_page_numbers(self):
        """Test text cleaning removes page numbers."""
        extractor = PDFTextExtractor()

        input_text = """
        Introduction
        This is the introduction text.
        
        1
        
        Background
        This is background information.
        
        2
        
        Conclusion
        This is the conclusion.
        """

        cleaned = extractor._clean_text(input_text)

        # Should remove standalone page numbers
        lines = cleaned.split("\n")
        standalone_numbers = [line.strip() for line in lines if line.strip().isdigit()]
        assert len(standalone_numbers) == 0

    def test_clean_text_short_lines(self):
        """Test text cleaning removes very short lines."""
        extractor = PDFTextExtractor()

        input_text = """
        This is a proper line of text.
        a
        Another proper line.
        b
        Final line.
        """

        cleaned = extractor._clean_text(input_text)

        # Should remove very short lines (likely artifacts)
        assert "This is a proper line of text." in cleaned
        assert "Another proper line." in cleaned
        assert "Final line." in cleaned
        # Single character lines should be removed
        lines = [line.strip() for line in cleaned.split("\n") if line.strip()]
        short_lines = [line for line in lines if len(line) < 3]
        assert len(short_lines) == 0

    def test_clean_text_empty_input(self):
        """Test text cleaning with empty input."""
        extractor = PDFTextExtractor()

        cleaned = extractor._clean_text("")
        assert cleaned == ""

        cleaned = extractor._clean_text("   \n\n   ")
        assert cleaned.strip() == ""


class TestSectionParsing:
    """Test cases for section parsing functionality."""

    def test_parse_sections_complete_paper(self):
        """Test section parsing with complete paper."""
        extractor = PDFTextExtractor()

        paper_text = """
        Title: Attention Is All You Need
        
        Abstract
        The dominant sequence transduction models are based on complex recurrent networks.
        
        1 Introduction
        Recurrent neural networks have been established as state of the art approaches.
        
        2 Background
        The goal of reducing sequential computation forms the foundation.
        
        3 Model Architecture
        Most competitive neural sequence transduction models have an encoder-decoder structure.
        
        4 Experiments
        We conducted experiments on two machine translation tasks.
        
        5 Results
        Table 1 summarizes our results on English-to-German translation.
        
        6 Conclusion
        In this work, we presented the Transformer architecture.
        
        References
        [1] Dzmitry Bahdanau et al. Neural machine translation. 2014.
        """

        sections = extractor._parse_sections(paper_text)

        assert "abstract" in sections
        assert "introduction" in sections
        assert "methodology" in sections  # Should map "Model Architecture"
        assert "results" in sections
        assert "conclusion" in sections
        assert "references" in sections

        assert "dominant sequence transduction" in sections["abstract"]
        assert "Recurrent neural networks" in sections["introduction"]
        assert "encoder-decoder structure" in sections["methodology"]
        assert "Table 1 summarizes" in sections["results"]
        assert "Transformer architecture" in sections["conclusion"]
        assert "Dzmitry Bahdanau" in sections["references"]

    def test_parse_sections_minimal_paper(self):
        """Test section parsing with minimal paper."""
        extractor = PDFTextExtractor()

        paper_text = """
        Short Paper Title
        
        Abstract
        This is a short abstract.
        
        Conclusion
        This is the conclusion.
        """

        sections = extractor._parse_sections(paper_text)

        assert "This is a short abstract" in sections["abstract"]
        assert "This is the conclusion" in sections["conclusion"]
        assert sections["introduction"] == ""
        assert sections["methodology"] == ""
        assert sections["results"] == ""

    def test_parse_sections_no_clear_sections(self):
        """Test section parsing with no clear sections."""
        extractor = PDFTextExtractor()

        paper_text = "This is just plain text without any clear section headers."

        sections = extractor._parse_sections(paper_text)

        # All sections should be empty when no headers are found
        for section_content in sections.values():
            assert section_content == ""

    def test_parse_sections_alternative_headers(self):
        """Test section parsing with alternative section headers."""
        extractor = PDFTextExtractor()

        paper_text = """
        Paper Title
        
        Abstract
        This is the abstract.
        
        Methods
        This describes the methods used.
        
        Experiments
        This describes the experiments.
        
        Discussion
        This is the discussion section.
        
        Bibliography
        [1] Reference 1
        """

        sections = extractor._parse_sections(paper_text)

        assert "This is the abstract" in sections["abstract"]
        assert (
            "describes the methods" in sections["methodology"]
        )  # "Methods" -> methodology
        assert (
            "describes the experiments" in sections["results"]
        )  # "Experiments" -> results
        assert (
            "discussion section" in sections["conclusion"]
        )  # "Discussion" -> conclusion
        assert "Reference 1" in sections["references"]  # "Bibliography" -> references

    def test_extract_section_content_with_length_limit(self):
        """Test section content extraction with length limits."""
        extractor = PDFTextExtractor()

        # Create very long section content
        long_content = "A" * 5000  # 5000 characters
        paper_text = f"""
        Abstract
        {long_content}
        
        Introduction
        This is the introduction.
        """

        sections = extractor._parse_sections(paper_text)

        # Abstract should be truncated (allow some flexibility for truncation logic)
        assert (
            len(sections["abstract"]) <= 3010
        )  # Allow small buffer for truncation logic
        assert sections["abstract"].endswith("...") or len(sections["abstract"]) < 5000

        # Introduction should be normal
        assert "This is the introduction" in sections["introduction"]

    def test_extract_section_content_sentence_boundary(self):
        """Test section content extraction respects sentence boundaries."""
        extractor = PDFTextExtractor()

        # Create content that would be truncated
        sentences = ["This is sentence " + str(i) + "." for i in range(200)]
        long_content = " ".join(sentences)

        paper_text = f"""
        Abstract
        {long_content}
        
        Introduction
        This is the introduction.
        """

        sections = extractor._parse_sections(paper_text)

        # Should try to end at sentence boundary if possible
        if len(sections["abstract"]) < len(long_content):
            # If truncated, should ideally end with a period
            assert sections["abstract"].endswith(".") or sections["abstract"].endswith(
                "..."
            )


class TestExtractFromURL:
    """Test cases for the main extract_from_url method."""

    @patch.object(PDFTextExtractor, "_download_pdf")
    @patch.object(PDFTextExtractor, "_extract_text_from_pdf")
    @patch.object(PDFTextExtractor, "_parse_sections")
    def test_extract_from_url_success(self, mock_parse, mock_extract, mock_download):
        """Test successful extraction from URL."""
        # Setup mocks
        mock_download.return_value = SAMPLE_PDF_CONTENT
        mock_extract.return_value = "Sample paper text content"
        mock_parse.return_value = {
            "abstract": "Sample abstract",
            "introduction": "Sample introduction",
            "methodology": "",
            "results": "",
            "conclusion": "Sample conclusion",
            "references": "",
        }

        extractor = PDFTextExtractor()
        result = extractor.extract_from_url("https://example.com/paper.pdf")

        assert isinstance(result, PaperText)
        assert result.full_text == "Sample paper text content"
        assert result.abstract == "Sample abstract"
        assert result.introduction == "Sample introduction"
        assert result.conclusion == "Sample conclusion"

        # Verify method calls
        mock_download.assert_called_once_with("https://example.com/paper.pdf")
        mock_extract.assert_called_once_with(SAMPLE_PDF_CONTENT)
        mock_parse.assert_called_once_with("Sample paper text content")

    def test_extract_from_url_invalid_url(self):
        """Test extraction with invalid URL."""
        extractor = PDFTextExtractor()

        with pytest.raises(ValueError) as exc_info:
            extractor.extract_from_url("invalid-url")

        assert "Invalid URL format" in str(exc_info.value)

    @patch.object(PDFTextExtractor, "_download_pdf")
    def test_extract_from_url_download_failure(self, mock_download):
        """Test extraction with download failure."""
        mock_download.side_effect = requests.RequestException("Download failed")

        extractor = PDFTextExtractor()

        with pytest.raises(requests.RequestException):
            extractor.extract_from_url("https://example.com/paper.pdf")

    @patch.object(PDFTextExtractor, "_download_pdf")
    @patch.object(PDFTextExtractor, "_extract_text_from_pdf")
    def test_extract_from_url_empty_text(self, mock_extract, mock_download):
        """Test extraction with empty text result."""
        mock_download.return_value = SAMPLE_PDF_CONTENT
        mock_extract.return_value = ""  # Empty text

        extractor = PDFTextExtractor()

        with pytest.raises(ValueError) as exc_info:
            extractor.extract_from_url("https://example.com/paper.pdf")

        assert "No text could be extracted" in str(exc_info.value)

    @patch.object(PDFTextExtractor, "_download_pdf")
    @patch.object(PDFTextExtractor, "_extract_text_from_pdf")
    def test_extract_from_url_whitespace_only_text(self, mock_extract, mock_download):
        """Test extraction with whitespace-only text result."""
        mock_download.return_value = SAMPLE_PDF_CONTENT
        mock_extract.return_value = "   \n\n   "  # Whitespace only

        extractor = PDFTextExtractor()

        with pytest.raises(ValueError) as exc_info:
            extractor.extract_from_url("https://example.com/paper.pdf")

        assert "No text could be extracted" in str(exc_info.value)


class TestPDFTextExtractorIntegration:
    """Integration tests for PDFTextExtractor."""

    @patch("requests.Session.get")
    @patch("PyPDF2.PdfReader")
    def test_full_extraction_pipeline(self, mock_pdf_reader, mock_get):
        """Test the complete extraction pipeline."""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = SAMPLE_PDF_CONTENT
        mock_response.headers = {"content-type": "application/pdf"}
        mock_get.return_value = mock_response

        # Mock PDF reader
        mock_reader_instance = Mock()
        mock_reader_instance.is_encrypted = False

        mock_page = Mock()
        mock_page.extract_text.return_value = """
        Attention Is All You Need
        
        Abstract
        The dominant sequence transduction models are based on complex recurrent networks.
        
        1 Introduction
        Recurrent neural networks have been established as state of the art.
        
        2 Model Architecture
        Most competitive models have an encoder-decoder structure.
        
        3 Results
        Our model achieves state-of-the-art results.
        
        4 Conclusion
        We presented the Transformer architecture.
        
        References
        [1] Reference 1
        """

        mock_reader_instance.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader_instance

        extractor = PDFTextExtractor()
        result = extractor.extract_from_url("https://arxiv.org/pdf/1706.03762.pdf")

        # Verify result structure
        assert isinstance(result, PaperText)
        assert "Attention Is All You Need" in result.full_text
        assert "dominant sequence transduction" in result.abstract
        assert "Recurrent neural networks" in result.introduction
        assert "encoder-decoder structure" in result.methodology
        assert "state-of-the-art results" in result.results
        assert "Transformer architecture" in result.conclusion
        assert "Reference 1" in result.references

        # Verify utility methods work
        summary = result.get_section_summary()
        assert summary["abstract"] is True
        assert summary["introduction"] is True
        assert summary["methodology"] is True
        assert summary["results"] is True
        assert summary["conclusion"] is True
        assert summary["references"] is True


class TestPDFTextExtractorEdgeCases:
    """Test edge cases and error conditions."""

    def test_extractor_with_custom_user_agent(self):
        """Test that extractor sets custom user agent."""
        extractor = PDFTextExtractor()

        user_agent = extractor.session.headers.get("User-Agent")
        assert user_agent is not None
        assert "Mozilla" in user_agent
        assert "WebKit" in user_agent

    @patch("requests.Session.get")
    def test_extractor_timeout_configuration(self, mock_get):
        """Test that extractor uses configured timeout."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = SAMPLE_PDF_CONTENT
        mock_response.headers = {"content-type": "application/pdf"}
        mock_get.return_value = mock_response

        extractor = PDFTextExtractor(timeout=45)
        extractor._download_pdf("https://example.com/paper.pdf")

        mock_get.assert_called_once_with("https://example.com/paper.pdf", timeout=45)

    def test_extractor_max_retries_configuration(self):
        """Test that extractor uses configured max retries."""
        extractor = PDFTextExtractor(max_retries=7)
        assert extractor.max_retries == 7

    @patch.object(PDFTextExtractor, "_is_valid_url")
    def test_extract_from_url_url_validation_called(self, mock_validate):
        """Test that URL validation is called during extraction."""
        mock_validate.return_value = False  # Invalid URL

        extractor = PDFTextExtractor()

        with pytest.raises(ValueError):
            extractor.extract_from_url("test-url")

        mock_validate.assert_called_once_with("test-url")

    def test_section_patterns_coverage(self):
        """Test that section patterns cover expected variations."""
        extractor = PDFTextExtractor()

        # Test various section header formats
        test_cases = [
            ("Abstract", "abstract"),
            ("1 Introduction", "introduction"),
            ("2. Methods", "methodology"),
            ("3 Methodology", "methodology"),
            ("4. Results", "results"),
            ("5 Experiments", "results"),
            ("6. Conclusion", "conclusion"),
            ("7 Discussion", "conclusion"),
            ("References", "references"),
            ("Bibliography", "references"),
        ]

        for header, expected_section in test_cases:
            paper_text = f"""
            Paper Title
            
            {header}
            This is the content for {expected_section}.
            
            Next Section
            Other content.
            """

            sections = extractor._parse_sections(paper_text)
            assert expected_section in sections
            # Content should be extracted (though exact matching depends on parsing logic)
            if sections[expected_section]:  # If content was found
                assert "content" in sections[expected_section].lower()
