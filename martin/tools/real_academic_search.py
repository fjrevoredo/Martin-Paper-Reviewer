"""
Real Academic Search Engine

Integrates arXiv and Semantic Scholar APIs to provide real literature search
functionality, replacing the mock academic search engine.
"""

import os
import re
from dataclasses import dataclass
from typing import List, Optional

from .arxiv_client import ArxivClient, ArxivPaper
from .semantic_scholar_client import SemanticScholarClient, SemanticScholarPaper


@dataclass
class SearchResult:
    """
    Standardized search result format compatible with existing DSPy signatures.
    Maintains compatibility with the existing mock AcademicSearchEngine interface.
    """

    title: str
    authors: List[str]
    abstract: str
    year: int
    venue: str
    citation_count: int
    relevance_score: float
    url: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dict format expected by existing DSPy signatures."""
        return {
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract,
            "year": self.year,
            "venue": self.venue,
            "citation_count": self.citation_count,
            "relevance_score": self.relevance_score,
            "url": self.url,
        }


class RealAcademicSearch:
    """
    Real academic search engine that queries arXiv and Semantic Scholar APIs.

    This class replaces the mock AcademicSearchEngine with real academic data
    while maintaining the same interface for compatibility with existing code.
    """

    def __init__(self, max_results: int = 10):
        """
        Initialize the real academic search engine.

        Args:
            max_results: Maximum number of results to return per search
        """
        self.max_results = max_results

        # Initialize API clients
        self.arxiv_client = ArxivClient()

        # Get Semantic Scholar API key from environment (optional)
        semantic_scholar_api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
        self.semantic_scholar_client = SemanticScholarClient(
            api_key=semantic_scholar_api_key
        )

        print(f"RealAcademicSearch initialized with max_results={max_results}")
        if semantic_scholar_api_key:
            print("Using Semantic Scholar API key for higher rate limits")

    def search(self, query: str) -> List[SearchResult]:
        """
        Search both arXiv and Semantic Scholar for papers matching the query.

        Args:
            query: Search query string

        Returns:
            List of SearchResult objects, deduplicated and ranked by relevance
        """
        print(f"Searching for: '{query}'")

        all_results = []

        # Search arXiv
        try:
            arxiv_papers = self.arxiv_client.search(
                query, max_results=self.max_results // 2
            )
            arxiv_results = [
                self._convert_arxiv_paper(paper, query) for paper in arxiv_papers
            ]
            all_results.extend(arxiv_results)
            print(f"Found {len(arxiv_results)} papers from arXiv")
        except Exception as e:
            print(f"📚 arXiv search hit a snag, but I'll keep looking elsewhere: {e}")

        # Search Semantic Scholar
        try:
            ss_papers = self.semantic_scholar_client.search(
                query, max_results=self.max_results // 2
            )
            ss_results = [
                self._convert_semantic_scholar_paper(paper, query)
                for paper in ss_papers
            ]
            all_results.extend(ss_results)
            print(f"Found {len(ss_results)} papers from Semantic Scholar")
        except Exception as e:
            print(
                f"📖 Semantic Scholar search had some trouble, but no worries - I've got other sources: {e}"
            )

        # Deduplicate and rank results
        deduplicated_results = self._deduplicate_results(all_results)
        ranked_results = self._rank_results(deduplicated_results, query)

        # Limit to max_results
        final_results = ranked_results[: self.max_results]

        print(f"Returning {len(final_results)} deduplicated and ranked results")
        return final_results

    def _convert_arxiv_paper(self, paper: ArxivPaper, query: str) -> SearchResult:
        """Convert ArxivPaper to SearchResult format."""
        # Extract year from published date
        year = self._extract_year_from_date(paper.published)

        # Calculate relevance score
        relevance_score = self._calculate_relevance_score(
            paper.title, paper.abstract, query
        )

        # Determine venue from categories
        venue = self._format_arxiv_venue(paper.categories)

        return SearchResult(
            title=paper.title,
            authors=paper.authors,
            abstract=paper.abstract,
            year=year,
            venue=venue,
            citation_count=0,  # arXiv doesn't provide citation counts
            relevance_score=relevance_score,
            url=paper.pdf_url,
        )

    def _convert_semantic_scholar_paper(
        self, paper: SemanticScholarPaper, query: str
    ) -> SearchResult:
        """Convert SemanticScholarPaper to SearchResult format."""
        # Calculate relevance score
        relevance_score = self._calculate_relevance_score(
            paper.title, paper.abstract, query
        )

        return SearchResult(
            title=paper.title,
            authors=paper.authors,
            abstract=paper.abstract,
            year=paper.year,
            venue=paper.venue,
            citation_count=paper.citation_count,
            relevance_score=relevance_score,
            url=paper.url,
        )

    def _extract_year_from_date(self, date_string: str) -> int:
        """Extract year from arXiv date string."""
        if not date_string:
            return 2024

        try:
            # arXiv dates are in format: 2023-12-15T10:30:00Z
            year_match = re.match(r"(\d{4})", date_string)
            if year_match:
                return int(year_match.group(1))
        except:
            pass

        return 2024

    def _format_arxiv_venue(self, categories: List[str]) -> str:
        """Format arXiv categories into a readable venue string."""
        if not categories:
            return "arXiv preprint"

        # Map common arXiv categories to readable names
        category_map = {
            "cs.AI": "Computer Science - Artificial Intelligence",
            "cs.CL": "Computer Science - Computation and Language",
            "cs.CV": "Computer Science - Computer Vision",
            "cs.LG": "Computer Science - Machine Learning",
            "cs.NE": "Computer Science - Neural Networks",
            "stat.ML": "Statistics - Machine Learning",
            "math.ST": "Mathematics - Statistics Theory",
            "physics": "Physics",
            "q-bio": "Quantitative Biology",
        }

        primary_category = categories[0]
        readable_name = category_map.get(primary_category, primary_category)
        return f"arXiv preprint ({readable_name})"

    def _calculate_relevance_score(
        self, title: str, abstract: str, query: str
    ) -> float:
        """
        Calculate relevance score based on query term matches in title and abstract.

        Args:
            title: Paper title
            abstract: Paper abstract
            query: Search query

        Returns:
            Relevance score between 0.0 and 1.0
        """
        if not query:
            return 0.5

        # Normalize text for comparison
        title_lower = title.lower()
        abstract_lower = abstract.lower()
        query_lower = query.lower()

        # Extract query terms
        query_terms = [
            term.strip()
            for term in re.split(r"[^\w]+", query_lower)
            if len(term.strip()) > 2
        ]

        if not query_terms:
            return 0.5

        # Calculate matches
        title_matches = sum(1 for term in query_terms if term in title_lower)
        abstract_matches = sum(1 for term in query_terms if term in abstract_lower)

        # Weight title matches more heavily
        title_score = (title_matches / len(query_terms)) * 0.7
        abstract_score = (abstract_matches / len(query_terms)) * 0.3

        total_score = title_score + abstract_score

        # Ensure score is between 0.0 and 1.0
        return min(1.0, max(0.0, total_score))

    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """
        Remove duplicate papers based on title similarity.

        Args:
            results: List of search results

        Returns:
            Deduplicated list of search results
        """
        if not results:
            return results

        deduplicated = []
        seen_titles = set()

        for result in results:
            # Normalize title for comparison
            normalized_title = self._normalize_title(result.title)

            # Check if we've seen a similar title
            is_duplicate = False
            for seen_title in seen_titles:
                if self._titles_are_similar(normalized_title, seen_title):
                    is_duplicate = True
                    break

            if not is_duplicate:
                deduplicated.append(result)
                seen_titles.add(normalized_title)

        return deduplicated

    def _normalize_title(self, title: str) -> str:
        """Normalize title for deduplication comparison."""
        if not title:
            return ""

        # Convert to lowercase and remove special characters
        normalized = re.sub(r"[^\w\s]", " ", title.lower())
        # Remove extra whitespace
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized

    def _titles_are_similar(
        self, title1: str, title2: str, threshold: float = 0.8
    ) -> bool:
        """
        Check if two titles are similar enough to be considered duplicates.

        Uses a simple word overlap metric.
        """
        if not title1 or not title2:
            return False

        words1 = set(title1.split())
        words2 = set(title2.split())

        if not words1 or not words2:
            return False

        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        similarity = intersection / union if union > 0 else 0
        return similarity >= threshold

    def _rank_results(
        self, results: List[SearchResult], query: str
    ) -> List[SearchResult]:
        """
        Rank results by relevance score and citation count.

        Args:
            results: List of search results
            query: Original search query

        Returns:
            Sorted list of search results
        """

        def ranking_key(result: SearchResult) -> tuple:
            # Primary sort by relevance score (descending)
            # Secondary sort by citation count (descending)
            # Tertiary sort by year (descending, prefer recent papers)
            return (-result.relevance_score, -result.citation_count, -result.year)

        return sorted(results, key=ranking_key)
