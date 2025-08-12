"""
Martin - Your Research Paper Reviewer Buddy

A comprehensive, modular pipeline that automates the analysis and evaluation
of academic research papers using the DSPy framework.
"""

__version__ = "0.1.0"
__author__ = "Martin Team"

from .models.paper_text import PaperText

# Import main DSPy module
from .paper_reviewer import PaperReviewer

# Import DSPy signatures
from .signatures import (
    ContributionAnalysis,
    FinalVerdict,
    GenerateSearchQueries,
    ImpactAssessment,
    InitialExtraction,
    LiteratureComparison,
    MethodologyAnalysis,
    SocialMediaPromotion,
)
from .tools.academic_search import AcademicSearchEngine, SearchResult

# Import implemented components
from .tools.pdf_extractor import PDFTextExtractor

__all__ = [
    "PDFTextExtractor",
    "AcademicSearchEngine",
    "SearchResult",
    "PaperText",
    "InitialExtraction",
    "MethodologyAnalysis",
    "ContributionAnalysis",
    "GenerateSearchQueries",
    "LiteratureComparison",
    "ImpactAssessment",
    "FinalVerdict",
    "SocialMediaPromotion",
    "PaperReviewer",
]
