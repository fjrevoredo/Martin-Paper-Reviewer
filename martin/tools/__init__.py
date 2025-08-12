"""
Tools package for Martin

Contains external tools for PDF processing and academic search functionality.
"""

from .academic_search import AcademicSearchEngine, SearchResult
from .pdf_extractor import PDFTextExtractor

__all__ = ["PDFTextExtractor", "AcademicSearchEngine", "SearchResult"]
