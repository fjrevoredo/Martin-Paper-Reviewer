"""
Data models package

Contains Pydantic models for structured data throughout the pipeline.
"""

from .paper_text import PaperText

# from .analysis_results import AnalysisResults  # Will be implemented in later tasks
# from .social_content import SocialContent      # Will be implemented in later tasks

__all__ = ["PaperText"]
