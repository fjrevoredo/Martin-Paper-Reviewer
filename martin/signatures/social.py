"""
DSPy signatures for social media content generation.

Contains signatures for generating social media content to promote
valuable research papers on platforms like Twitter and LinkedIn.
"""

from typing import List

import dspy


class SocialMediaPromotion(dspy.Signature):
    """
    Generate social media content for valuable papers.

    This signature creates engaging social media content for papers
    that have been deemed worth promoting, helping researchers share
    important findings with their networks.
    """

    title: str = dspy.InputField(desc="The title of the research paper")

    key_takeaways: List[str] = dspy.InputField(
        desc="Main findings and insights from the paper that should be highlighted"
    )

    field_impact: dict = dspy.InputField(
        desc="Assessment of the paper's potential impact on the research field"
    )

    twitter_thread: List[str] = dspy.OutputField(
        desc="Twitter thread draft as a list of tweets (max 280 chars each), starting with an engaging hook and covering key findings"
    )

    linkedin_post: str = dspy.OutputField(
        desc="LinkedIn post draft (1-2 paragraphs) with professional tone, highlighting the research significance and practical implications"
    )
