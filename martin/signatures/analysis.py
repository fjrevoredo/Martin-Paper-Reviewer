"""
DSPy signatures for paper analysis components.

Contains signatures for analyzing methodology and contributions
of research papers with detailed assessments.
"""

from typing import List

import dspy


class MethodologyAnalysis(dspy.Signature):
    """
    Analyze research methodology and assess reproducibility.

    This signature evaluates the methodological approach used in the paper,
    identifying strengths and weaknesses, and provides a reproducibility
    score with detailed justification.
    """

    methodology_section: str = dspy.InputField(
        desc="The methodology, methods, or approach section of the paper"
    )

    methodological_strengths: List[str] = dspy.OutputField(
        desc="List of identified strengths in the methodology, such as rigorous experimental design, appropriate statistical methods, or clear protocols"
    )

    methodological_weaknesses: List[str] = dspy.OutputField(
        desc="List of identified weaknesses in the methodology, such as small sample sizes, missing controls, or unclear procedures"
    )

    reproducibility_assessment: dict = dspy.OutputField(
        desc="Dictionary containing 'score' (integer 1-10) and 'justification' (string) explaining the reproducibility rating based on method clarity, data availability, and implementation details"
    )


class ContributionAnalysis(dspy.Signature):
    """
    Identify and evaluate claimed contributions.

    This signature analyzes the introduction and conclusion sections
    to extract claimed contributions and assess their novelty and
    significance to the field.
    """

    introduction: str = dspy.InputField(
        desc="The introduction section of the paper where contributions are typically outlined"
    )

    conclusion: str = dspy.InputField(
        desc="The conclusion section of the paper where contributions are summarized"
    )

    claimed_contributions: List[str] = dspy.OutputField(
        desc="List of contributions explicitly claimed by the authors, such as new algorithms, theoretical insights, or empirical findings"
    )

    novelty_assessment: dict = dspy.OutputField(
        desc="Dictionary mapping each contribution to its novelty assessment, including 'novelty_score' (1-10), 'significance_score' (1-10), and 'justification' explaining the assessment"
    )
