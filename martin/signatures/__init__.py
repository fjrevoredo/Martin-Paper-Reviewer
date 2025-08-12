"""
DSPy Signatures package

Contains all DSPy signature definitions for the paper review pipeline.
"""

from .analysis import ContributionAnalysis, MethodologyAnalysis
from .assessment import FinalVerdict, ImpactAssessment
from .extraction import InitialExtraction
from .literature import GenerateSearchQueries, LiteratureComparison
from .social import SocialMediaPromotion

__all__ = [
    "InitialExtraction",
    "MethodologyAnalysis",
    "ContributionAnalysis",
    "GenerateSearchQueries",
    "LiteratureComparison",
    "ImpactAssessment",
    "FinalVerdict",
    "SocialMediaPromotion",
]
