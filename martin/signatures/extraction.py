"""
DSPy signatures for initial paper content extraction.

Contains signatures for extracting bibliographic information
and basic metadata from research papers.
"""

from typing import List

import dspy


class InitialExtraction(dspy.Signature):
    """
    Extract basic bibliographic information from research paper text.

    This signature processes the full paper text to identify and extract
    key bibliographic elements like title, authors, abstract, and keywords.
    """

    paper_text: str = dspy.InputField(
        desc="Full text of the research paper including all sections"
    )

    title: str = dspy.OutputField(desc="The main title of the research paper")

    authors: List[str] = dspy.OutputField(
        desc="List of author names in the order they appear in the paper"
    )

    abstract: str = dspy.OutputField(desc="The paper's abstract or summary section")

    keywords: List[str] = dspy.OutputField(
        desc="Key terms, concepts, and technical keywords that represent the paper's main topics"
    )
