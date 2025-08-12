"""
Semantic Scholar API Client

Provides access to Semantic Scholar's academic paper database.
Handles JSON parsing and converts to standard format.
"""

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests


@dataclass
class SemanticScholarPaper:
    """Raw paper data from Semantic Scholar API"""

    title: str
    authors: List[str]
    abstract: str
    year: int
    venue: str
    citation_count: int
    paper_id: str
    url: Optional[str] = None
    doi: Optional[str] = None
    fields_of_study: List[str] = None


class SemanticScholarClient:
    """
    Client for searching Semantic Scholar papers using their official API.

    API Documentation: https://api.semanticscholar.org/
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.semanticscholar.org/graph/v1",
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()

        # Set up headers
        headers = {
            "User-Agent": "DSPy-Paper-Reviewer/1.0 (https://github.com/dspy-paper-reviewer)"
        }
        if api_key:
            headers["x-api-key"] = api_key

        self.session.headers.update(headers)

        # Rate limiting (free tier: 100 requests per 5 minutes)
        self.last_request_time = 0
        self.min_request_interval = (
            3.0 if not api_key else 0.1
        )  # 3 seconds for free tier

    def search(self, query: str, max_results: int = 10) -> List[SemanticScholarPaper]:
        """
        Search Semantic Scholar for papers matching the query.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of SemanticScholarPaper objects

        Raises:
            requests.RequestException: If API request fails
            ValueError: If response cannot be parsed
        """
        # Rate limiting
        self._wait_for_rate_limit()

        # Prepare search parameters
        params = {
            "query": query,
            "limit": min(max_results, 100),  # API limit is 100
            "fields": "title,authors,abstract,year,venue,citationCount,paperId,url,externalIds,fieldsOfStudy",
        }

        try:
            response = self.session.get(
                f"{self.base_url}/paper/search", params=params, timeout=30
            )

            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                print(
                    f"Rate limited by Semantic Scholar, waiting {retry_after} seconds..."
                )
                time.sleep(retry_after)
                response = self.session.get(
                    f"{self.base_url}/paper/search", params=params, timeout=30
                )

            response.raise_for_status()

            return self._parse_response(response.json())

        except requests.RequestException as e:
            raise requests.RequestException(
                f"📖 I'm having trouble connecting to Semantic Scholar right now. Their API might be taking a little break - let's try again soon! (Semantic Scholar API request failed: {e})"
            )
        except Exception as e:
            raise ValueError(
                f"🤔 Semantic Scholar sent me something I wasn't expecting. Sometimes their response format changes slightly! (Failed to parse Semantic Scholar response: {e})"
            )

    def _wait_for_rate_limit(self):
        """Implement simple rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _parse_response(self, json_data: Dict[str, Any]) -> List[SemanticScholarPaper]:
        """
        Parse Semantic Scholar API JSON response.

        Args:
            json_data: JSON response from Semantic Scholar API

        Returns:
            List of parsed SemanticScholarPaper objects
        """
        papers = []

        # Check if response has the expected structure
        if "data" not in json_data:
            return papers

        for item in json_data["data"]:
            try:
                paper = self._parse_paper(item)
                if paper:
                    papers.append(paper)
            except Exception as e:
                # Skip malformed entries but continue processing
                print(
                    f"📝 Heads up: I skipped one entry from Semantic Scholar that had unusual formatting: {e}"
                )
                continue

        return papers

    def _parse_paper(self, item: Dict[str, Any]) -> Optional[SemanticScholarPaper]:
        """Parse a single paper from Semantic Scholar response."""
        try:
            # Extract title
            title = item.get("title", "").strip()
            if not title:
                return None

            # Extract authors
            authors = []
            author_list = item.get("authors", [])
            if author_list:
                for author in author_list:
                    if isinstance(author, dict) and "name" in author:
                        authors.append(author["name"])
                    elif isinstance(author, str):
                        authors.append(author)

            # Extract abstract
            abstract = item.get("abstract", "").strip()
            if not abstract:
                abstract = "No abstract available"

            # Extract year
            year = item.get("year")
            if not year or not isinstance(year, int):
                year = 2024  # Default to current year

            # Extract venue
            venue = item.get("venue", "").strip()
            if not venue:
                venue = "Unknown Venue"

            # Extract citation count
            citation_count = item.get("citationCount", 0)
            if not isinstance(citation_count, int):
                citation_count = 0

            # Extract paper ID
            paper_id = item.get("paperId", "")

            # Extract URL
            url = item.get("url")

            # Extract DOI
            doi = None
            external_ids = item.get("externalIds", {})
            if external_ids and isinstance(external_ids, dict):
                doi = external_ids.get("DOI")

            # Extract fields of study
            fields_of_study = []
            fields = item.get("fieldsOfStudy", [])
            if fields and isinstance(fields, list):
                fields_of_study = [field for field in fields if isinstance(field, str)]

            return SemanticScholarPaper(
                title=title,
                authors=authors,
                abstract=abstract,
                year=year,
                venue=venue,
                citation_count=citation_count,
                paper_id=paper_id,
                url=url,
                doi=doi,
                fields_of_study=fields_of_study,
            )

        except Exception as e:
            print(
                f"📄 I had trouble parsing one paper from Semantic Scholar - skipping it to keep things moving: {e}"
            )
            return None

    def get_paper_details(self, paper_id: str) -> Optional[SemanticScholarPaper]:
        """
        Get detailed information for a specific paper by ID.

        Args:
            paper_id: Semantic Scholar paper ID

        Returns:
            SemanticScholarPaper object or None if not found
        """
        self._wait_for_rate_limit()

        try:
            response = self.session.get(
                f"{self.base_url}/paper/{paper_id}",
                params={
                    "fields": "title,authors,abstract,year,venue,citationCount,paperId,url,externalIds,fieldsOfStudy"
                },
                timeout=30,
            )

            if response.status_code == 404:
                return None

            response.raise_for_status()
            return self._parse_paper(response.json())

        except requests.RequestException as e:
            print(
                f"📋 Couldn't grab the details for one paper, but that's okay - I'll keep working with what I have: {e}"
            )
            return None
