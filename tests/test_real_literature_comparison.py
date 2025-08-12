"""
Tests for real literature comparison functionality.

Tests the arXiv client, Semantic Scholar client, and integrated RealAcademicSearch.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
import requests

from martin.tools.arxiv_client import ArxivClient, ArxivPaper
from martin.tools.real_academic_search import RealAcademicSearch, SearchResult
from martin.tools.semantic_scholar_client import (
    SemanticScholarClient,
    SemanticScholarPaper,
)


class TestArxivClient:
    """Test cases for ArxivClient."""

    def test_init(self):
        """Test ArxivClient initialization."""
        client = ArxivClient()
        assert client.base_url == "http://export.arxiv.org/api/query"
        assert client.session is not None

    def test_prepare_query(self):
        """Test query preparation for arXiv API."""
        client = ArxivClient()

        # Test normal query
        query = client._prepare_query("transformer attention mechanism")
        assert "transformer" in query
        assert "attention" in query
        assert "mechanism" in query

        # Test empty query
        query = client._prepare_query("")
        assert query == "all:machine learning"

        # Test query with special characters
        query = client._prepare_query("neural-networks & deep learning!")
        assert "neural" in query
        assert "networks" in query

    def test_clean_text(self):
        """Test text cleaning functionality."""
        client = ArxivClient()

        # Test normal text
        cleaned = client._clean_text("  This is   a test  \n  ")
        assert cleaned == "This is a test"

        # Test empty text
        cleaned = client._clean_text("")
        assert cleaned == ""

        # Test None
        cleaned = client._clean_text(None)
        assert cleaned == ""

    def test_extract_year(self):
        """Test year extraction from date strings."""
        client = ArxivClient()

        # Test valid date
        year = client._extract_year("2023-12-15T10:30:00Z")
        assert year == 2023

        # Test invalid date
        year = client._extract_year("invalid-date")
        assert year == 2024

        # Test empty date
        year = client._extract_year("")
        assert year == 2024

    @patch("requests.Session.get")
    def test_search_success(self, mock_get):
        """Test successful arXiv search."""
        # Mock response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = """<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <id>http://arxiv.org/abs/2301.00001v1</id>
                <title>Test Paper Title</title>
                <summary>This is a test abstract.</summary>
                <published>2023-01-01T00:00:00Z</published>
                <updated>2023-01-01T00:00:00Z</updated>
                <author><name>Test Author</name></author>
                <category term="cs.AI" />
            </entry>
        </feed>"""
        mock_get.return_value = mock_response

        client = ArxivClient()
        results = client.search("test query", max_results=1)

        assert len(results) == 1
        assert results[0].title == "Test Paper Title"
        assert results[0].abstract == "This is a test abstract."
        assert "Test Author" in results[0].authors
        assert results[0].arxiv_id == "2301.00001v1"

    @patch("requests.Session.get")
    def test_search_network_error(self, mock_get):
        """Test arXiv search with network error."""
        mock_get.side_effect = requests.RequestException("Network error")

        client = ArxivClient()
        with pytest.raises(requests.RequestException):
            client.search("test query")


class TestSemanticScholarClient:
    """Test cases for SemanticScholarClient."""

    def test_init_without_api_key(self):
        """Test SemanticScholarClient initialization without API key."""
        client = SemanticScholarClient()
        assert client.api_key is None
        assert client.min_request_interval == 3.0

    def test_init_with_api_key(self):
        """Test SemanticScholarClient initialization with API key."""
        client = SemanticScholarClient(api_key="test-key")
        assert client.api_key == "test-key"
        assert client.min_request_interval == 0.1

    @patch("requests.Session.get")
    def test_search_success(self, mock_get):
        """Test successful Semantic Scholar search."""
        # Mock response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "title": "Test Paper",
                    "authors": [{"name": "Test Author"}],
                    "abstract": "Test abstract",
                    "year": 2023,
                    "venue": "Test Conference",
                    "citationCount": 10,
                    "paperId": "test-id",
                    "url": "https://example.com",
                    "externalIds": {"DOI": "10.1000/test"},
                    "fieldsOfStudy": ["Computer Science"],
                }
            ]
        }
        mock_get.return_value = mock_response

        client = SemanticScholarClient()
        results = client.search("test query", max_results=1)

        assert len(results) == 1
        assert results[0].title == "Test Paper"
        assert results[0].authors == ["Test Author"]
        assert results[0].year == 2023
        assert results[0].citation_count == 10

    @patch("requests.Session.get")
    def test_search_rate_limit(self, mock_get):
        """Test Semantic Scholar search with rate limiting."""
        # Mock rate limit response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "1"}
        mock_response.raise_for_status.side_effect = requests.HTTPError("Rate limited")
        mock_get.return_value = mock_response

        client = SemanticScholarClient()
        with pytest.raises(requests.RequestException):
            client.search("test query")

    @patch("requests.Session.get")
    def test_search_network_error(self, mock_get):
        """Test Semantic Scholar search with network error."""
        mock_get.side_effect = requests.RequestException("Network error")

        client = SemanticScholarClient()
        with pytest.raises(requests.RequestException):
            client.search("test query")


class TestRealAcademicSearch:
    """Test cases for RealAcademicSearch integration."""

    def test_init(self):
        """Test RealAcademicSearch initialization."""
        search = RealAcademicSearch(max_results=5)
        assert search.max_results == 5
        assert search.arxiv_client is not None
        assert search.semantic_scholar_client is not None

    def test_convert_arxiv_paper(self):
        """Test conversion of ArxivPaper to SearchResult."""
        search = RealAcademicSearch()

        arxiv_paper = ArxivPaper(
            title="Test Paper",
            authors=["Author 1", "Author 2"],
            abstract="Test abstract",
            published="2023-01-01T00:00:00Z",
            updated="2023-01-01T00:00:00Z",
            arxiv_id="2301.00001v1",
            pdf_url="https://arxiv.org/pdf/2301.00001v1.pdf",
            categories=["cs.AI"],
        )

        result = search._convert_arxiv_paper(arxiv_paper, "test query")

        assert result.title == "Test Paper"
        assert result.authors == ["Author 1", "Author 2"]
        assert result.year == 2023
        assert result.citation_count == 0  # arXiv doesn't provide citations
        assert "arXiv preprint" in result.venue
        assert result.url == "https://arxiv.org/pdf/2301.00001v1.pdf"

    def test_convert_semantic_scholar_paper(self):
        """Test conversion of SemanticScholarPaper to SearchResult."""
        search = RealAcademicSearch()

        ss_paper = SemanticScholarPaper(
            title="Test Paper",
            authors=["Author 1"],
            abstract="Test abstract",
            year=2023,
            venue="Test Conference",
            citation_count=15,
            paper_id="test-id",
            url="https://example.com",
        )

        result = search._convert_semantic_scholar_paper(ss_paper, "test query")

        assert result.title == "Test Paper"
        assert result.authors == ["Author 1"]
        assert result.year == 2023
        assert result.venue == "Test Conference"
        assert result.citation_count == 15
        assert result.url == "https://example.com"

    def test_calculate_relevance_score(self):
        """Test relevance score calculation."""
        search = RealAcademicSearch()

        # Test exact match in title
        score = search._calculate_relevance_score(
            "Transformer Attention Mechanism",
            "This paper discusses transformers",
            "transformer attention",
        )
        assert score > 0.5

        # Test no match
        score = search._calculate_relevance_score(
            "Unrelated Paper", "About something else", "transformer attention"
        )
        assert score < 0.5

        # Test empty query
        score = search._calculate_relevance_score("Test Paper", "Test abstract", "")
        assert score == 0.5

    def test_normalize_title(self):
        """Test title normalization for deduplication."""
        search = RealAcademicSearch()

        # Test normal title
        normalized = search._normalize_title("Attention Is All You Need!")
        assert normalized == "attention is all you need"

        # Test title with special characters
        normalized = search._normalize_title(
            "BERT: Pre-training of Deep Bidirectional Transformers"
        )
        assert normalized == "bert pre training of deep bidirectional transformers"

        # Test empty title
        normalized = search._normalize_title("")
        assert normalized == ""

    def test_titles_are_similar(self):
        """Test title similarity detection."""
        search = RealAcademicSearch()

        # Test similar titles (adjust threshold for this test)
        similar = search._titles_are_similar(
            "attention is all you need",
            "attention is all you need for translation",
            threshold=0.6,  # Lower threshold for this test
        )
        assert similar

        # Test dissimilar titles
        similar = search._titles_are_similar(
            "attention is all you need", "bert pre training transformers"
        )
        assert not similar

        # Test empty titles
        similar = search._titles_are_similar("", "test")
        assert not similar

    def test_deduplicate_results(self):
        """Test result deduplication."""
        search = RealAcademicSearch()

        results = [
            SearchResult("Attention Is All You Need", [], "", 2023, "", 0, 0.9),
            SearchResult(
                "Attention Is All You Need!", [], "", 2023, "", 0, 0.8
            ),  # Duplicate
            SearchResult("BERT Pre-training", [], "", 2022, "", 0, 0.7),
        ]

        deduplicated = search._deduplicate_results(results)

        assert len(deduplicated) == 2
        assert "Attention Is All You Need" in deduplicated[0].title
        assert "BERT Pre-training" in deduplicated[1].title

    def test_rank_results(self):
        """Test result ranking."""
        search = RealAcademicSearch()

        results = [
            SearchResult(
                "Paper A", [], "", 2020, "", 5, 0.5
            ),  # Low relevance, low citations
            SearchResult(
                "Paper B", [], "", 2023, "", 100, 0.9
            ),  # High relevance, high citations
            SearchResult(
                "Paper C", [], "", 2022, "", 50, 0.8
            ),  # Medium relevance, medium citations
        ]

        ranked = search._rank_results(results, "test query")

        # Should be ranked by relevance first, then citations, then year
        assert ranked[0].title == "Paper B"  # Highest relevance
        assert ranked[1].title == "Paper C"  # Medium relevance
        assert ranked[2].title == "Paper A"  # Lowest relevance

    @patch.object(ArxivClient, "search")
    @patch.object(SemanticScholarClient, "search")
    def test_search_integration(self, mock_ss_search, mock_arxiv_search):
        """Test integrated search functionality."""
        # Mock arXiv results
        mock_arxiv_search.return_value = [
            ArxivPaper(
                title="arXiv Paper",
                authors=["Author 1"],
                abstract="Test abstract",
                published="2023-01-01T00:00:00Z",
                updated="2023-01-01T00:00:00Z",
                arxiv_id="2301.00001v1",
                pdf_url="https://arxiv.org/pdf/2301.00001v1.pdf",
                categories=["cs.AI"],
            )
        ]

        # Mock Semantic Scholar results
        mock_ss_search.return_value = [
            SemanticScholarPaper(
                title="SS Paper",
                authors=["Author 2"],
                abstract="Test abstract",
                year=2023,
                venue="Test Conference",
                citation_count=10,
                paper_id="test-id",
                url="https://example.com",
            )
        ]

        search = RealAcademicSearch(max_results=10)
        results = search.search("test query")

        assert len(results) == 2
        assert any("arXiv Paper" in r.title for r in results)
        assert any("SS Paper" in r.title for r in results)

    @patch.object(ArxivClient, "search")
    @patch.object(SemanticScholarClient, "search")
    def test_search_with_api_failures(self, mock_ss_search, mock_arxiv_search):
        """Test search behavior when APIs fail."""
        # Mock arXiv failure
        mock_arxiv_search.side_effect = Exception("arXiv API failed")

        # Mock successful Semantic Scholar
        mock_ss_search.return_value = [
            SemanticScholarPaper(
                title="SS Paper",
                authors=["Author 1"],
                abstract="Test abstract",
                year=2023,
                venue="Test Conference",
                citation_count=10,
                paper_id="test-id",
                url="https://example.com",
            )
        ]

        search = RealAcademicSearch(max_results=10)
        results = search.search("test query")

        # Should still return Semantic Scholar results
        assert len(results) == 1
        assert results[0].title == "SS Paper"

    def test_search_result_to_dict(self):
        """Test SearchResult to_dict conversion for DSPy compatibility."""
        result = SearchResult(
            title="Test Paper",
            authors=["Author 1", "Author 2"],
            abstract="Test abstract",
            year=2023,
            venue="Test Conference",
            citation_count=10,
            relevance_score=0.9,
            url="https://example.com",
        )

        result_dict = result.to_dict()

        expected_keys = [
            "title",
            "authors",
            "abstract",
            "year",
            "venue",
            "citation_count",
            "relevance_score",
            "url",
        ]
        assert all(key in result_dict for key in expected_keys)
        assert result_dict["title"] == "Test Paper"
        assert result_dict["citation_count"] == 10


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_arxiv_malformed_xml(self):
        """Test arXiv client with malformed XML."""
        client = ArxivClient()

        with pytest.raises(ValueError):
            client._parse_response("invalid xml")

    def test_semantic_scholar_empty_response(self):
        """Test Semantic Scholar client with empty response."""
        client = SemanticScholarClient()

        results = client._parse_response({"data": []})
        assert len(results) == 0

    def test_semantic_scholar_malformed_response(self):
        """Test Semantic Scholar client with malformed response."""
        client = SemanticScholarClient()

        results = client._parse_response({})  # Missing 'data' key
        assert len(results) == 0

    @patch.object(ArxivClient, "search")
    @patch.object(SemanticScholarClient, "search")
    def test_search_both_apis_fail(self, mock_ss_search, mock_arxiv_search):
        """Test search behavior when both APIs fail."""
        mock_arxiv_search.side_effect = Exception("arXiv failed")
        mock_ss_search.side_effect = Exception("Semantic Scholar failed")

        search = RealAcademicSearch(max_results=10)
        results = search.search("test query")

        # Should return empty list when both APIs fail
        assert len(results) == 0


if __name__ == "__main__":
    pytest.main([__file__])
