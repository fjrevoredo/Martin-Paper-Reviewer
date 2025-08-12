"""
DSPy signatures for impact assessment and final verdict.

Contains signatures for evaluating the potential impact of research
and generating final recommendations with detailed justification.
"""

from typing import List

import dspy


class ImpactAssessment(dspy.Signature):
    """
    Assess potential impact of the research.

    This signature evaluates both the potential field impact and broader
    societal impact of the research based on the complete analysis
    performed in previous steps.
    """

    paper_analysis_summary: dict = dspy.InputField(
        desc="Combined analysis results from methodology, contribution, and other assessment steps"
    )

    literature_comparison: dict = dspy.InputField(
        desc="Results from literature comparison showing how the paper relates to existing work"
    )

    field_impact: dict = dspy.OutputField(
        desc="Assessment of potential impact on the research field, including 'impact_score' (1-10), 'reasoning', and 'specific_areas' that may be affected"
    )

    societal_impact: dict = dspy.OutputField(
        desc="Assessment of potential broader societal impact, including 'impact_score' (1-10), 'reasoning', and 'application_areas' where the research might be applied"
    )


class FinalVerdict(dspy.Signature):
    """
    Provide final recommendation with justification.

    This signature synthesizes all previous analysis to provide a final
    recommendation on whether the paper is worth reading, along with
    detailed justification and key takeaways.
    """

    full_analysis: dict = dspy.InputField(
        desc="Complete analysis results from all previous steps including methodology, contributions, literature comparison, and impact assessment"
    )

    recommendation: str = dspy.OutputField(
        desc="Final recommendation level: 'Highly Recommended', 'Worth Reading', 'Proceed with Caution', 'Should be Ignored', or 'Critically Flawed'"
    )

    justification: str = dspy.OutputField(
        desc="Detailed reasoning for the recommendation, explaining the key factors that led to this assessment"
    )

    worth_reading_verdict: bool = dspy.OutputField(
        desc="Binary recommendation: True if the paper is worth reading, False otherwise"
    )

    key_takeaways: List[str] = dspy.OutputField(
        desc="List of 3-5 main points or insights that readers should know about this paper, useful for quick reference"
    )
