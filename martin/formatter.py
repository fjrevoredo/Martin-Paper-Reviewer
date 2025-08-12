"""
Structured Output Formatter for Martin

Formats paper review results into friendly, readable Markdown output
with Martin's personality and conversational tone throughout.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import dspy


class MarkdownFormatter:
    """
    Formats paper review results with Martin's friendly personality.

    Provides warm, conversational formatting with:
    - Martin's friendly introduction and closing
    - Conversational section headers
    - Personal commentary and encouragement
    - Easy-to-read advice from a knowledgeable friend
    """

    def __init__(self, include_toc: bool = True, include_metadata: bool = True):
        """
        Initialize the Markdown formatter.

        Args:
            include_toc: Whether to include a table of contents
            include_metadata: Whether to include review metadata
        """
        self.include_toc = include_toc
        self.include_metadata = include_metadata

    def format_review(self, result: dspy.Prediction, pdf_url: str) -> str:
        """
        Format a complete paper review into Markdown.

        Args:
            result: The PaperReviewer prediction result
            pdf_url: The original PDF URL

        Returns:
            Formatted Markdown string
        """
        sections = []

        # Header
        sections.append(self._format_header(result, pdf_url))

        # Table of Contents (if enabled)
        if self.include_toc:
            sections.append(self._format_table_of_contents(result))

        # Executive Summary
        sections.append(self._format_executive_summary(result))

        # Paper Information
        if hasattr(result, "extraction") and result.extraction:
            sections.append(self._format_paper_information(result.extraction))

        # Methodology Analysis
        if hasattr(result, "methodology") and result.methodology:
            sections.append(self._format_methodology_analysis(result.methodology))

        # Contribution Analysis
        if hasattr(result, "contributions") and result.contributions:
            sections.append(self._format_contribution_analysis(result.contributions))

        # Literature Comparison
        if hasattr(result, "literature") and result.literature:
            sections.append(self._format_literature_comparison(result.literature))

        # Impact Assessment
        if hasattr(result, "impact") and result.impact:
            sections.append(self._format_impact_assessment(result.impact))

        # Final Verdict
        if hasattr(result, "verdict") and result.verdict:
            sections.append(self._format_final_verdict(result.verdict))

        # Social Media Content (if generated)
        if (
            hasattr(result, "social_media")
            and result.social_media
            and result.social_media.get("generated")
        ):
            sections.append(self._format_social_media_content(result.social_media))

        # Review Metadata (if enabled)
        if self.include_metadata:
            sections.append(self._format_review_metadata(result))

        # Martin's signature and closing
        sections.append(self._format_martin_closing())

        return "\n\n".join(sections)

    def _format_header(self, result: Any, pdf_url: str) -> str:
        """Format Martin's friendly review header."""
        # Try to get paper title from extraction results
        paper_title = "this fascinating paper"
        if hasattr(result, "extraction") and result.extraction:
            extracted_title = result.extraction.get("title", "")
            if extracted_title:
                paper_title = f'"{extracted_title}"'

        header = f"# 🤓 Martin's Review: {paper_title}\n\n"
        header += f"Hey there! I just finished reading through this paper, and I'm excited to share my thoughts with you.\n\n"

        header += f"**Paper:** {pdf_url}\n"
        header += f"**Reviewed by:** Martin, your research paper reviewer buddy\n"
        header += f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

        # Add friendly status indicator
        if hasattr(result, "success"):
            if result.success:
                header += f"**Status:** ✅ Complete analysis - I covered everything!\n"
            else:
                header += f"**Status:** ⚠️ Partial analysis - I did my best with what I could access\n"

        header += "\n---\n"

        return header

    def _format_table_of_contents(self, result: Any) -> str:
        """Format Martin's friendly table of contents."""
        toc = "## 📋 What I'll Cover\n\n"
        toc += "Here's what I discovered during my deep dive into this research:\n\n"

        sections = [
            "1. [Quick Summary](#quick-summary) - My first impressions",
            "2. [About This Paper](#about-this-paper) - The basics you need to know",
            "3. [How They Did It](#how-they-did-it) - Methodology breakdown",
            "4. [What's New Here](#whats-new-here) - Their contributions",
            "5. [How It Fits](#how-it-fits) - Comparison with other work",
            "6. [Why It Matters](#why-it-matters) - Impact assessment",
            "7. [My Final Take](#my-final-take) - Bottom line recommendation",
        ]

        # Add social media section if present
        if (
            hasattr(result, "social_media")
            and result.social_media
            and result.social_media.get("generated")
        ):
            sections.append(
                "8. [Share the Love](#share-the-love) - Social media content"
            )

        # Add metadata section if enabled
        if self.include_metadata:
            sections.append(
                "9. [Behind the Scenes](#behind-the-scenes) - Review details"
            )

        toc += "\n".join(sections)
        return toc

    def _format_executive_summary(self, result: Any) -> str:
        """Format Martin's friendly executive summary."""
        summary = "## 📋 Quick Summary\n\n"
        summary += "Here's what caught my attention right away:\n\n"

        # Get key information for summary
        recommendation = "Still thinking about it"
        worth_reading = "Let me tell you"

        if hasattr(result, "verdict") and result.verdict:
            recommendation = result.verdict.get(
                "recommendation", "Still thinking about it"
            )
            worth_reading = (
                "Absolutely!"
                if result.verdict.get("worth_reading")
                else "Maybe skip this one"
            )

        # Friendly summary box
        summary += "### My Quick Take\n\n"
        summary += f"| What I Think | My Assessment |\n"
        summary += f"|--------------|---------------|\n"
        summary += f"| **My Recommendation** | {recommendation} |\n"
        summary += f"| **Should You Read It?** | {worth_reading} |\n"

        # Add scores with friendly context
        if hasattr(result, "methodology") and result.methodology:
            repro_score = result.methodology.get("reproducibility_score", "N/A")
            summary += f"| **Can You Reproduce This?** | {repro_score}/10 |\n"

        if hasattr(result, "impact") and result.impact:
            field_score = result.impact.get("field_impact_score", "N/A")
            societal_score = result.impact.get("societal_impact_score", "N/A")
            summary += f"| **Impact on the Field** | {field_score}/10 |\n"
            summary += f"| **Real-World Impact** | {societal_score}/10 |\n"

        return summary

    def _format_paper_information(self, extraction: Dict) -> str:
        """Format paper information with Martin's friendly touch."""
        info = "## 📄 About This Paper\n\n"
        info += "Let me tell you what this research is all about:\n\n"

        title = extraction.get("title", "The title was a bit tricky to extract")
        authors = extraction.get("authors", [])
        keywords = extraction.get("keywords", [])
        abstract = extraction.get("abstract", "")

        info += f"**What it's called:** {title}\n\n"

        if authors:
            if len(authors) <= 5:
                info += f"**Who wrote it:** {', '.join(authors)}\n\n"
            else:
                info += f"**Who wrote it:** {', '.join(authors[:5])} and {len(authors) - 5} other brilliant minds\n\n"

        if keywords:
            info += f"**Key topics:** {', '.join(keywords[:10])}\n\n"

        # Show actual abstract content with friendly intro
        if abstract:
            info += f"### What They Say It's About\n\n"
            info += f"Here's how the authors describe their work:\n\n"
            # Limit abstract length for readability
            if len(abstract) > 500:
                info += f"{abstract[:500]}...\n\n"
                info += f"*(I trimmed this a bit for readability - the full abstract is in the original paper!)*\n\n"
            else:
                info += f"{abstract}\n\n"

        return info

    def _format_methodology_analysis(self, methodology: Dict) -> str:
        """Format methodology analysis with Martin's friendly perspective."""
        analysis = "## 🔬 How They Did It\n\n"
        analysis += "Let me break down their approach and whether you could replicate this work:\n\n"

        # Reproducibility assessment
        repro_assessment = methodology.get("reproducibility_assessment", {})
        repro_score = repro_assessment.get("score", "N/A")
        repro_justification = repro_assessment.get("justification", "")

        analysis += f"### Could You Do This Too?\n\n"
        analysis += f"**My reproducibility score:** {repro_score}/10\n\n"

        if repro_justification:
            analysis += f"**Here's why:** {repro_justification}\n\n"

        # Methodological strengths
        strengths = methodology.get("methodological_strengths", [])
        if strengths:
            analysis += f"### What They Did Really Well\n\n"
            for i, strength in enumerate(strengths, 1):
                analysis += f"{i}. {strength}\n"
            analysis += "\n"

        # Methodological weaknesses
        weaknesses = methodology.get("methodological_weaknesses", [])
        if weaknesses:
            analysis += f"### Where They Could Improve\n\n"
            for i, weakness in enumerate(weaknesses, 1):
                analysis += f"{i}. {weakness}\n"
            analysis += "\n"

        # Assessment interpretation with Martin's voice
        if repro_score != "N/A":
            try:
                score_val = int(repro_score) if str(repro_score).isdigit() else 0
                if score_val >= 8:
                    interpretation = "Fantastic! You could definitely replicate this work with the details they provided."
                elif score_val >= 6:
                    interpretation = "Pretty good! You might need to fill in a few gaps, but it's doable."
                elif score_val >= 4:
                    interpretation = "It's possible, but you'd need to do some detective work to figure out the missing pieces."
                else:
                    interpretation = "Honestly, this would be tough to replicate. They're missing some crucial details."

                analysis += f"### My Take on Reproducibility\n\n"
                analysis += f"**Bottom line:** {interpretation}\n\n"
            except:
                pass

        return analysis

    def _format_contribution_analysis(self, contributions: Dict) -> str:
        """Format contribution analysis with Martin's friendly assessment."""
        analysis = "## 💡 What's New Here\n\n"
        analysis += "Here's what the authors claim they've brought to the table:\n\n"

        claimed_contributions = contributions.get("claimed_contributions", [])
        novelty_assessment = contributions.get("novelty_assessment", {})

        # List claimed contributions
        if claimed_contributions:
            analysis += f"### What They Say They've Done\n\n"
            for i, contribution in enumerate(claimed_contributions, 1):
                analysis += f"{i}. {contribution}\n"
            analysis += "\n"

        # Show novelty assessments with friendly language
        if novelty_assessment and isinstance(novelty_assessment, dict):
            analysis += f"### My Take on Each Contribution\n\n"
            for contribution, assessment in novelty_assessment.items():
                if isinstance(assessment, dict):
                    novelty_score = assessment.get("novelty_score", "N/A")
                    significance_score = assessment.get("significance_score", "N/A")
                    justification = assessment.get("justification", "")

                    analysis += f"**{contribution}:**\n"
                    analysis += f"- How new is it? {novelty_score}/10\n"
                    analysis += f"- How important is it? {significance_score}/10\n"
                    if justification:
                        analysis += f"- My thoughts: {justification}\n"
                    analysis += "\n"

        # Summary with Martin's voice
        contrib_count = len(claimed_contributions)
        if contrib_count > 0:
            analysis += f"### The Big Picture\n\n"
            if contrib_count == 1:
                analysis += (
                    f"They're making one main claim about what's new in their work. "
                )
            else:
                analysis += f"They're claiming {contrib_count} different contributions to the field. "
            analysis += f"I've looked at each one to see how novel and significant it really is. "
            analysis += f"Sometimes researchers are a bit optimistic about their contributions, so I try to give you the honest truth!\n\n"

        return analysis

    def _format_literature_comparison(self, literature: Dict) -> str:
        """Format literature comparison with Martin's friendly perspective."""
        comparison = "## 📚 How It Fits\n\n"
        comparison += "I did some digging to see how this work relates to what's already out there:\n\n"

        papers_found = literature.get("papers_found", 0)
        queries_used = literature.get("queries_used", 0)
        comparison_completed = literature.get("comparison_completed", False)

        # Search queries used
        search_queries = literature.get("search_queries", [])
        if search_queries:
            comparison += f"### What I Searched For\n\n"
            comparison += f"I used these search terms to find related work:\n\n"
            for i, query in enumerate(search_queries, 1):
                comparison += f'{i}. "{query}"\n'
            comparison += "\n"

        # Related papers found
        search_results = literature.get("search_results", [])
        if search_results:
            comparison += f"### Similar Papers I Found\n\n"
            comparison += f"Here are the most relevant papers I discovered:\n\n"
            for i, paper in enumerate(search_results[:5], 1):  # Show top 5
                title = paper.get("title", "Unknown Title")
                authors = paper.get("authors", [])
                year = paper.get("year", "Unknown")
                relevance = paper.get("relevance_score", 0)

                comparison += f"{i}. **{title}** ({year})\n"
                if authors:
                    comparison += f"   - By: {', '.join(authors[:3])}{'...' if len(authors) > 3 else ''}\n"
                comparison += f"   - How similar: {relevance:.2f}/10\n\n"

        # Analysis results with friendly language
        context = literature.get("context", "")
        differentiation = literature.get("differentiation", "")
        standing_in_field = literature.get("standing_in_field", "")

        if context:
            comparison += f"### The Research Landscape\n\n"
            comparison += f"{context}\n\n"

        if differentiation:
            comparison += f"### What Makes This Different\n\n"
            comparison += f"{differentiation}\n\n"

        if standing_in_field:
            comparison += f"### Where This Fits In\n\n"
            comparison += f"{standing_in_field}\n\n"

        # Summary with Martin's voice
        comparison += f"### My Literature Detective Work\n\n"
        comparison += f"- **Papers I found:** {papers_found}\n"
        comparison += f"- **Search strategies used:** {queries_used}\n"
        comparison += f"- **Analysis status:** {'All done!' if comparison_completed else 'Partially complete'}\n\n"

        if papers_found > 0:
            comparison += f"I found some interesting connections and differences that help put this work in context. "
            comparison += f"Understanding how research builds on previous work is crucial for evaluating its contribution!\n\n"

        return comparison

    def _format_impact_assessment(self, impact: Dict) -> str:
        """Format impact assessment with Martin's friendly perspective."""
        assessment = "## 🌟 Why It Matters\n\n"
        assessment += "Let me tell you about the potential impact of this work:\n\n"

        field_impact = impact.get("field_impact", {})
        societal_impact = impact.get("societal_impact", {})

        # Field impact analysis with friendly language
        if field_impact:
            field_score = field_impact.get("impact_score", "N/A")
            field_reasoning = field_impact.get("reasoning", "")
            field_areas = field_impact.get("specific_areas", [])

            assessment += f"### Impact on the Research Field\n\n"
            assessment += f"**My score:** {field_score}/10\n\n"

            if field_reasoning:
                assessment += f"**Here's my thinking:** {field_reasoning}\n\n"

            if field_areas:
                assessment += f"**Areas that could benefit:**\n"
                for area in field_areas:
                    assessment += f"- {area}\n"
                assessment += "\n"

        # Societal impact analysis with friendly language
        if societal_impact:
            societal_score = societal_impact.get("impact_score", "N/A")
            societal_reasoning = societal_impact.get("reasoning", "")
            application_areas = societal_impact.get("application_areas", [])

            assessment += f"### Real-World Impact\n\n"
            assessment += f"**My score:** {societal_score}/10\n\n"

            if societal_reasoning:
                assessment += f"**Why this matters:** {societal_reasoning}\n\n"

            if application_areas:
                assessment += f"**Where you might see this applied:**\n"
                for area in application_areas:
                    assessment += f"- {area}\n"
                assessment += "\n"

        # Summary table with Martin's friendly assessments
        field_score = field_impact.get("impact_score", "N/A") if field_impact else "N/A"
        societal_score = (
            societal_impact.get("impact_score", "N/A") if societal_impact else "N/A"
        )

        assessment += f"### Impact at a Glance\n\n"
        assessment += f"| Type of Impact | My Score | What This Means |\n"
        assessment += f"|----------------|----------|------------------|\n"

        field_assessment = self._get_friendly_impact_assessment(field_score)
        assessment += (
            f"| **For Researchers** | {field_score}/10 | {field_assessment} |\n"
        )

        societal_assessment = self._get_friendly_impact_assessment(societal_score)
        assessment += f"| **For Everyone Else** | {societal_score}/10 | {societal_assessment} |\n\n"

        return assessment

    def _get_impact_assessment(self, score: Any) -> str:
        """Get impact assessment text based on score."""
        if score == "N/A" or not str(score).replace(".", "").isdigit():
            return "Not assessed"

        score_val = float(score)
        if score_val >= 9:
            return "Revolutionary impact"
        elif score_val >= 7:
            return "Significant impact"
        elif score_val >= 5:
            return "Moderate impact"
        elif score_val >= 3:
            return "Limited impact"
        else:
            return "Minimal impact"

    def _get_friendly_impact_assessment(self, score: Any) -> str:
        """Get friendly impact assessment text based on score."""
        if score == "N/A" or not str(score).replace(".", "").isdigit():
            return "I couldn't assess this one"

        score_val = float(score)
        if score_val >= 9:
            return "This could change everything!"
        elif score_val >= 7:
            return "This is pretty exciting stuff"
        elif score_val >= 5:
            return "Solid contribution worth noting"
        elif score_val >= 3:
            return "Modest but meaningful impact"
        else:
            return "Limited impact, but still valuable"

    def _format_final_verdict(self, verdict: Dict) -> str:
        """Format final verdict with Martin's friendly recommendation."""
        final = "## 🎯 My Final Take\n\n"

        recommendation = verdict.get("recommendation", "Still thinking about it")
        worth_reading = verdict.get("worth_reading", False)
        justification = verdict.get("justification", "")
        key_takeaways = verdict.get("key_takeaways", [])

        # Recommendation with emoji and friendly language
        rec_emoji = self._get_recommendation_emoji(recommendation)
        final += f"### {rec_emoji} My Recommendation: {recommendation}\n\n"

        # Worth reading indicator with personality
        if worth_reading:
            reading_indicator = "✅ Absolutely! Add this to your reading list"
        else:
            reading_indicator = "❌ You might want to skip this one"
        final += f"**Should you read it?** {reading_indicator}\n\n"

        # Justification with Martin's voice
        if justification:
            final += f"### Here's Why I Think This\n\n"
            final += f"{justification}\n\n"

        # Key takeaways with friendly intro
        if key_takeaways:
            final += f"### What You Should Remember\n\n"
            final += (
                f"If you do read this paper, here are the main things to take away:\n\n"
            )
            for i, takeaway in enumerate(key_takeaways, 1):
                final += f"{i}. {takeaway}\n"
            final += "\n"

        # Summary with Martin's personality
        final += f"### The Bottom Line\n\n"
        final += f"After diving deep into this research, I'm giving it a '{recommendation}' rating. "
        final += f"I looked at everything - the methodology, what's new, how it fits with other work, and why it matters. "

        if worth_reading:
            final += f"I think you'll find value in reading this, especially if you're working in this area. "
            final += f"The authors have done solid work that contributes meaningfully to the field.\n\n"
        else:
            final += f"While the authors put effort into this work, there are some significant issues that limit its value. "
            final += (
                f"Your time might be better spent on other papers in this area.\n\n"
            )

        return final

    def _get_recommendation_emoji(self, recommendation: str) -> str:
        """Get emoji for recommendation level."""
        emoji_map = {
            "Highly Recommended": "🌟",
            "Worth Reading": "👍",
            "Proceed with Caution": "⚠️",
            "Should be Ignored": "👎",
            "Critically Flawed": "❌",
        }
        return emoji_map.get(recommendation, "📄")

    def _format_social_media_content(self, social_media: Dict) -> str:
        """Format social media content with Martin's friendly touch."""
        social = "## 📱 Share the Love\n\n"
        social += "I thought this research was worth sharing, so I whipped up some social media content for you:\n\n"

        twitter_thread = social_media.get("twitter_thread", [])
        linkedin_post = social_media.get("linkedin_post", "")

        # Twitter thread with friendly intro
        if twitter_thread:
            social += f"### Twitter Thread\n\n"
            social += f"Here's a thread you can share to spread the word:\n\n"
            for i, tweet in enumerate(twitter_thread, 1):
                social += f"**Tweet {i}:**\n"
                social += f"{tweet}\n\n"

        # LinkedIn post with friendly intro
        if linkedin_post:
            social += f"### LinkedIn Post\n\n"
            social += (
                f"And here's something more detailed for your professional network:\n\n"
            )
            social += f"{linkedin_post}\n\n"

        # Summary with Martin's voice
        twitter_length = len(twitter_thread)
        linkedin_length = len(linkedin_post)

        social += f"### Ready to Share!\n\n"
        social += f"- **Twitter thread:** {twitter_length} tweets ready to go\n"
        social += f"- **LinkedIn post:** {linkedin_length} characters of professional insight\n\n"

        social += f"I only create social content for research I think is genuinely worth sharing. "
        social += f"Feel free to use these as-is or adapt them to your own voice!\n\n"

        return social

    def _format_review_metadata(self, result: Any) -> str:
        """Format review metadata with Martin's friendly touch."""
        metadata = "## 🔍 Behind the Scenes\n\n"
        metadata += "Here's a peek at how I put this review together:\n\n"

        # Review status with friendly language
        success = getattr(result, "success", False)
        errors = getattr(result, "errors", [])
        warnings = getattr(result, "warnings", [])

        metadata += f"### How It Went\n\n"
        if success:
            metadata += f"- **Status:** ✅ Everything went smoothly!\n"
        else:
            metadata += f"- **Status:** ⚠️ I ran into a few bumps, but got through it\n"
        metadata += f"- **Issues I encountered:** {len(errors)}\n"
        metadata += f"- **Things to note:** {len(warnings)}\n\n"

        # Processing details with personality
        metadata += f"### My Analysis Process\n\n"

        # Count completed components
        components = [
            "paper_text",
            "extraction",
            "methodology",
            "contributions",
            "literature",
            "impact",
            "verdict",
            "social_media",
        ]
        completed = sum(
            1 for comp in components if hasattr(result, comp) and getattr(result, comp)
        )

        metadata += f"- **Analysis steps completed:** {completed}/{len(components)}\n"
        metadata += (
            f"- **Review finished:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        metadata += f"- **Powered by:** Martin (your friendly research buddy)\n\n"

        # Show errors with supportive language
        if errors:
            metadata += f"### Challenges I Faced\n\n"
            metadata += f"I encountered a few issues while analyzing this paper:\n\n"
            for i, error in enumerate(errors[:3], 1):  # Show max 3 errors
                metadata += f"{i}. {error}\n"
            if len(errors) > 3:
                metadata += f"... and {len(errors) - 3} other minor issues\n"
            metadata += "\nDon't worry - I worked around these problems to give you the best analysis I could!\n\n"

        return metadata

    def _format_martin_closing(self) -> str:
        """Format Martin's friendly closing message and signature."""
        closing = "---\n\n"
        closing += (
            "Thanks for letting me explore this fascinating research with you! 🤓\n\n"
        )
        closing += "I hope my analysis helps you understand what this paper is all about and whether it's worth your time. "
        closing += "Remember, research is a collaborative journey, and every paper - good or not-so-good - teaches us something.\n\n"
        closing += "If you have questions about my analysis or want to discuss any part of this review, "
        closing += "I'm always here to help!\n\n"
        closing += "Happy researching!\n\n"
        closing += "*- Martin* 📚✨"

        return closing


def format_paper_review(
    result: dspy.Prediction,
    pdf_url: str,
    include_toc: bool = True,
    include_metadata: bool = True,
) -> str:
    """
    Convenience function to format a paper review result with Martin's personality.

    Args:
        result: The PaperReviewer prediction result
        pdf_url: The original PDF URL
        include_toc: Whether to include Martin's friendly table of contents
        include_metadata: Whether to include review metadata

    Returns:
        Formatted Markdown string with Martin's friendly commentary
    """
    formatter = MarkdownFormatter(
        include_toc=include_toc, include_metadata=include_metadata
    )
    return formatter.format_review(result, pdf_url)
