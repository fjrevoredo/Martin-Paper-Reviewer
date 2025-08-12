"""
PDF Text Extraction Tool

Handles downloading and extracting structured text from PDF research papers.
Includes section parsing to identify key paper components.
"""

import re
import time
from io import BytesIO
from typing import Dict, List, Optional
from urllib.parse import urlparse

import PyPDF2
import requests

from ..models.paper_text import PaperText


class PDFTextExtractor:
    """
    Tool for extracting structured text from PDF research papers.

    Supports downloading from URLs and parsing into sections like
    abstract, introduction, methodology, results, and conclusion.
    """

    def __init__(self, timeout: int = 30, max_retries: int = 3):
        """
        Initialize PDF extractor with configuration.

        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

    def extract_from_url(self, pdf_url: str) -> PaperText:
        """
        Extract structured text from a PDF URL.

        Args:
            pdf_url: URL to the PDF file

        Returns:
            PaperText object with extracted and parsed content

        Raises:
            ValueError: If URL is invalid or PDF cannot be processed
            requests.RequestException: If download fails
        """
        # Validate URL
        if not self._is_valid_url(pdf_url):
            raise ValueError(
                f"🤔 Hmm, that URL doesn't look quite right to me. Could you double-check it? I want to make sure I can reach your paper! (Invalid URL format: {pdf_url})"
            )

        # Download PDF content
        pdf_content = self._download_pdf(pdf_url)

        # Extract text from PDF
        full_text = self._extract_text_from_pdf(pdf_content)

        if not full_text.strip():
            raise ValueError(
                "😅 I'm having trouble reading this PDF - it might be image-based or have some formatting that's tricky for me to parse. Could you try a different version? (No text could be extracted from the PDF)"
            )

        # Parse sections
        sections = self._parse_sections(full_text)

        return PaperText(
            full_text=full_text,
            abstract=sections.get("abstract", ""),
            introduction=sections.get("introduction", ""),
            methodology=sections.get("methodology", ""),
            results=sections.get("results", ""),
            conclusion=sections.get("conclusion", ""),
            references=sections.get("references", ""),
        )

    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def _download_pdf(self, url: str) -> bytes:
        """
        Download PDF content from URL with retry logic.

        Args:
            url: PDF URL to download

        Returns:
            PDF content as bytes

        Raises:
            requests.RequestException: If download fails after retries
        """
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()

                # Verify content type
                content_type = response.headers.get("content-type", "").lower()
                if "pdf" not in content_type and not url.endswith(".pdf"):
                    # Try anyway - some servers don't set proper content-type
                    pass

                return response.content

            except requests.RequestException as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    time.sleep(2**attempt)
                    continue
                break

        raise requests.RequestException(
            f"😔 I tried my best to download that paper, but the server seems to be having issues. "
            f"Maybe try again in a moment? Sometimes these things just need a little patience! "
            f"(Failed to download PDF after {self.max_retries} attempts: {last_exception})"
        )

    def _extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """
        Extract text from PDF bytes using PyPDF2.

        Args:
            pdf_content: PDF file content as bytes

        Returns:
            Extracted text as string

        Raises:
            ValueError: If PDF cannot be read or is password protected
        """
        try:
            pdf_file = BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            # Check if PDF is encrypted
            if pdf_reader.is_encrypted:
                raise ValueError(
                    "🔒 This PDF is password-protected, and I don't want to pry! Could you share an open-access version? "
                    "I promise I'll give it the same thorough analysis! (PDF is password-protected)"
                )

            # Extract text from all pages
            text_parts = []
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_parts.append(page_text)
                except Exception as e:
                    print(
                        f"📄 Just a heads up: I couldn't read page {page_num + 1}, but I'll keep going with the rest: {e}"
                    )
                    continue

            if not text_parts:
                raise ValueError(
                    "😅 I'm not finding any readable text in this PDF. It might be all images or have some unusual formatting. "
                    "Could you try a text-based version? (No readable text found in PDF)"
                )

            return "\n\n".join(text_parts)

        except PyPDF2.errors.PdfReadError as e:
            raise ValueError(
                f"😔 This PDF seems to be corrupted or in a format I can't read. Could you try re-downloading it or getting a fresh copy? (Invalid or corrupted PDF file: {e})"
            )
        except Exception as e:
            raise ValueError(
                f"😅 I ran into an unexpected issue while processing this PDF. Don't worry though - it's probably just a formatting quirk! (Error processing PDF: {e})"
            )

    def _parse_sections(self, text: str) -> Dict[str, str]:
        """
        Parse paper text into sections using pattern matching.

        Args:
            text: Full paper text

        Returns:
            Dictionary mapping section names to content
        """
        sections = {}

        # Clean and normalize text
        text = self._clean_text(text)

        # Define section patterns (case-insensitive, more precise)
        section_patterns = {
            "abstract": [r"abstract"],
            "introduction": [r"\d+\s+introduction", r"introduction"],
            "methodology": [
                r"\d+\.?\s+methodology",
                r"\d+\.?\s+methods?",
                r"\d+\.?\s+approach",
                r"\d+\.?\s+model",
                r"methodology",
                r"methods?",
                r"approach",
                r"model",
            ],
            "results": [
                r"\d+\.?\s+results",
                r"\d+\.?\s+experiments?",
                r"\d+\.?\s+evaluation",
                r"\d+\.?\s+findings",
                r"results",
                r"experiments?",
                r"evaluation",
            ],
            "conclusion": [
                r"\d+\.?\s+conclusions?",
                r"\d+\.?\s+discussion",
                r"\d+\.?\s+future\s+work",
                r"conclusions?",
                r"discussion",
                r"future\s+work",
            ],
            "references": [r"references", r"bibliography"],
        }

        # Extract each section
        for section_name, patterns in section_patterns.items():
            content = self._extract_section_content(text, patterns)
            sections[section_name] = content

        return sections

    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove page numbers and headers/footers
        lines = text.split("\n")
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            # Skip likely page numbers
            if re.match(r"^\d+$", line):
                continue
            # Skip very short lines that are likely artifacts
            if len(line) < 3:
                continue
            cleaned_lines.append(line)

        return "\n".join(cleaned_lines)

    def _extract_section_content(self, text: str, patterns: List[str]) -> str:
        """
        Extract content for a specific section using multiple patterns.

        Args:
            text: Full paper text
            patterns: List of regex patterns to match section headers

        Returns:
            Extracted section content
        """
        text_lower = text.lower()

        # Try each pattern to find section start
        section_start = None
        header_end = None

        for pattern in patterns:
            # Look for pattern as section header
            matches = list(re.finditer(pattern, text_lower))
            if matches:
                # Use the first match
                match = matches[0]
                section_start = match.start()
                header_end = match.end()
                break

        if section_start is None:
            return ""

        # Find the actual content start (skip the header line)
        content_start = header_end

        # Skip to next line after header
        next_newline = text.find("\n", content_start)
        if next_newline != -1:
            content_start = next_newline + 1

        # Find the end of the section (next major heading or end of text)
        section_end = len(text)

        # Look for next section headers after current section
        remaining_text = text_lower[content_start:]

        # Common section header patterns that indicate new sections
        next_section_patterns = [
            r"\n\d+\s+[a-z]",  # Numbered sections like "2 Background"
            r"\n\d+\.\d+\s+[a-z]",  # Subsections like "2.1 Overview"
            r"\nreferences\b",
            r"\nbibliography\b",
            r"\nacknowledgments?\b",
            r"\nappendix\b",
        ]

        earliest_next = len(remaining_text)
        for pattern in next_section_patterns:
            matches = list(re.finditer(pattern, remaining_text))
            if matches:
                # Use first match that's not too close to start
                for match in matches:
                    if match.start() > 50:  # Must be at least 50 chars into section
                        earliest_next = min(earliest_next, match.start())
                        break

        if earliest_next < len(remaining_text):
            section_end = content_start + earliest_next

        # Extract and clean section content
        section_content = text[content_start:section_end].strip()

        # Limit section length to avoid including too much content
        max_section_length = 3000  # Reasonable limit for most sections
        if len(section_content) > max_section_length:
            # Try to cut at a sentence boundary
            truncated = section_content[:max_section_length]
            last_period = truncated.rfind(".")
            if (
                last_period > max_section_length * 0.7
            ):  # If we can find a period in last 30%
                section_content = truncated[: last_period + 1]
            else:
                section_content = truncated + "..."

        return section_content
