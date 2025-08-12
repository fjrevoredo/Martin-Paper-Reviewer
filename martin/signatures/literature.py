"""
DSPy signatures for literature comparison and contextualization.

Contains signatures for generating search queries and comparing
papers against existing literature in the field.
"""

from typing import List

import dspy


class GenerateSearchQueries(dspy.Signature):
    """
    Generate effective search queries for literature comparison.

    This signature analyzes the paper's title and abstract to create
    targeted search queries that will find the most relevant related
    work for comparison purposes.
    """

    title: str = dspy.InputField(desc="The title of the research paper")

    abstract: str = dspy.InputField(desc="The abstract of the research paper")

    search_queries: List[str] = dspy.OutputField(
        desc="Ranked list of 3-5 search queries designed to find related work, ordered by expected relevance and specificity"
    )


class LiteratureComparison(dspy.Signature):
    """
    Compare paper against existing literature.

    This signature takes the paper's claimed contributions and compares
    them against related papers found through academic search to determine
    how the work fits within the existing research landscape.
    """

    claimed_contributions: List[str] = dspy.InputField(
        desc="List of contributions claimed by the paper being analyzed"
    )

    search_results: List[dict] = dspy.InputField(
        desc="List of related papers from academic search, each containing title, abstract, authors, year, and other metadata"
    )

    context: str = dspy.OutputField(
        desc="Explanation of how this paper fits within the current research landscape and builds upon existing work"
    )

    differentiation: str = dspy.OutputField(
        desc="Clear description of what makes this paper different from and advances beyond the related work"
    )

    standing_in_field: str = dspy.OutputField(
        desc="Assessment of the paper's position relative to existing work - whether it's incremental, significant, or groundbreaking"
    )
