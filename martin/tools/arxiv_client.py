"""
arXiv API Client

Provides access to arXiv papers through their official API.
Handles XML parsing and converts to standard SearchResult format.
"""

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Optional
from urllib.parse import quote

import requests


@dataclass
class ArxivPaper:
    """Raw paper data from arXiv API"""

    title: str
    authors: List[str]
    abstract: str
    published: str
    updated: str
    arxiv_id: str
    pdf_url: str
    categories: List[str]


class ArxivClient:
    """
    Client for searching arXiv papers using their official API.

    API Documentation: https://arxiv.org/help/api/user-manual
    """

    def __init__(self, base_url: str = "http://export.arxiv.org/api/query"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "DSPy-Paper-Reviewer/1.0 (https://github.com/dspy-paper-reviewer)"
            }
        )

    def search(self, query: str, max_results: int = 10) -> List[ArxivPaper]:
        """
        Search arXiv for papers matching the query.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of ArxivPaper objects

        Raises:
            requests.RequestException: If API request fails
            ValueError: If response cannot be parsed
        """
        # Clean and prepare query for arXiv API
        clean_query = self._prepare_query(query)

        params = {
            "search_query": clean_query,
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending",
        }

        try:
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()

            return self._parse_response(response.text)

        except requests.RequestException as e:
            raise requests.RequestException(
                f"📚 I'm having trouble reaching the arXiv database right now. Their servers might be busy - let's try again in a moment! (arXiv API request failed: {e})"
            )
        except Exception as e:
            raise ValueError(
                f"🤔 I got a response from arXiv, but it's in a format I wasn't expecting. This happens sometimes with their API! (Failed to parse arXiv response: {e})"
            )

    def _prepare_query(self, query: str) -> str:
        """
        Prepare query string for arXiv API.

        arXiv supports field-specific searches like:
        - ti:title words
        - au:author
        - abs:abstract words
        - all:all fields (default)
        """
        # Remove special characters that might break the query
        clean_query = re.sub(r"[^\w\s\-\.]", " ", query)

        # Split into words and create a search query
        words = clean_query.split()
        if not words:
            return "all:machine learning"  # Fallback query

        # Use 'all:' prefix to search all fields
        search_terms = []
        for word in words[:10]:  # Limit to 10 words to avoid overly complex queries
            if len(word) > 2:  # Skip very short words
                search_terms.append(word)

        if not search_terms:
            return "all:machine learning"

        # Create query - arXiv uses AND by default
        return f"all:{' AND '.join(search_terms)}"

    def _parse_response(self, xml_content: str) -> List[ArxivPaper]:
        """
        Parse arXiv API XML response.

        Args:
            xml_content: Raw XML response from arXiv API

        Returns:
            List of parsed ArxivPaper objects
        """
        try:
            root = ET.fromstring(xml_content)

            # Define namespaces used by arXiv API
            namespaces = {
                "atom": "http://www.w3.org/2005/Atom",
                "arxiv": "http://arxiv.org/schemas/atom",
            }

            papers = []
            entries = root.findall("atom:entry", namespaces)

            for entry in entries:
                try:
                    paper = self._parse_entry(entry, namespaces)
                    if paper:
                        papers.append(paper)
                except Exception as e:
                    # Skip malformed entries but continue processing
                    print(f"Warning: Failed to parse arXiv entry: {e}")
                    continue

            return papers

        except ET.ParseError as e:
            raise ValueError(f"Invalid XML response from arXiv: {e}")

    def _parse_entry(self, entry: ET.Element, namespaces: dict) -> Optional[ArxivPaper]:
        """Parse a single entry from arXiv response."""
        try:
            # Extract title
            title_elem = entry.find("atom:title", namespaces)
            if title_elem is None or not title_elem.text:
                return None
            title = self._clean_text(title_elem.text)

            # Extract authors
            authors = []
            author_elems = entry.findall("atom:author", namespaces)
            for author_elem in author_elems:
                name_elem = author_elem.find("atom:name", namespaces)
                if name_elem is not None and name_elem.text:
                    authors.append(name_elem.text.strip())

            # Extract abstract
            summary_elem = entry.find("atom:summary", namespaces)
            if summary_elem is None or not summary_elem.text:
                return None
            abstract = self._clean_text(summary_elem.text)

            # Extract dates
            published_elem = entry.find("atom:published", namespaces)
            updated_elem = entry.find("atom:updated", namespaces)
            published = published_elem.text if published_elem is not None else ""
            updated = updated_elem.text if updated_elem is not None else ""

            # Extract arXiv ID from the ID field
            id_elem = entry.find("atom:id", namespaces)
            arxiv_id = ""
            pdf_url = ""
            if id_elem is not None and id_elem.text:
                # ID format: http://arxiv.org/abs/1234.5678v1
                arxiv_id = id_elem.text.split("/")[-1]  # Get the last part
                pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

            # Extract categories
            categories = []
            category_elems = entry.findall("atom:category", namespaces)
            for cat_elem in category_elems:
                term = cat_elem.get("term")
                if term:
                    categories.append(term)

            return ArxivPaper(
                title=title,
                authors=authors,
                abstract=abstract,
                published=published,
                updated=updated,
                arxiv_id=arxiv_id,
                pdf_url=pdf_url,
                categories=categories,
            )

        except Exception as e:
            print(f"Error parsing arXiv entry: {e}")
            return None

    def _clean_text(self, text: str) -> str:
        """Clean text by removing extra whitespace and newlines."""
        if not text:
            return ""

        # Replace multiple whitespace with single space
        cleaned = re.sub(r"\s+", " ", text.strip())
        return cleaned

    def _extract_year(self, date_string: str) -> int:
        """Extract year from arXiv date string."""
        if not date_string:
            return 2024  # Default to current year

        try:
            # arXiv dates are in format: 2023-12-15T10:30:00Z
            year_match = re.match(r"(\d{4})", date_string)
            if year_match:
                return int(year_match.group(1))
        except:
            pass

        return 2024  # Default fallback
