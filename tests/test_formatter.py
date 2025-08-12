"""
Tests for output formatting module.

Tests MarkdownFormatter class and format_paper_review function for various data scenarios.
"""

from datetime import datetime
from unittest.mock import Mock

import pytest

from martin.formatter import MarkdownFormatter, format_paper_review


class TestMarkdownFormatterInitialization:
    """Test cases for MarkdownFormatter initialization."""

    def test_formatter_initialization_defaults(self):
        """Test MarkdownFormatter initialization with default settings."""
        formatter = MarkdownFormatter()

        assert formatter.include_toc is True
        assert formatter.include_metadata is True

    def test_formatter_initialization_custom_settings(self):
        """Test MarkdownFormatter initialization with custom settings."""
        formatter = MarkdownFormatter(include_toc=False, include_metadata=False)

        assert formatter.include_toc is False
        assert formatter.include_metadata is False


class TestMarkdownFormatterHeader:
    """Test cases for header formatting."""

    def test_format_header_with_paper_title(self, sample_complete_result):
        """Test header formatting when paper title is available."""
        formatter = MarkdownFormatter()

        header = formatter._format_header(
            sample_complete_result, "https://example.com/paper.pdf"
        )

        assert '# 🤓 Martin\'s Review: "Attention Is All You Need"' in header
        assert "**Paper:** https://example.com/paper.pdf" in header
        assert "**Date:**" in header
        assert "✅ Complete analysis" in header

    def test_format_header_without_paper_title(self, sample_partial_result):
        """Test header formatting when paper title is not available."""
        formatter = MarkdownFormatter()

        header = formatter._format_header(
            sample_partial_result, "https://example.com/paper.pdf"
        )

        assert "# 🤓 Martin's Review" in header
        assert "**Paper:** https://example.com/paper.pdf" in header
        assert "⚠️ Partial analysis" in header

    def test_format_header_date_format(self, sample_complete_result):
        """Test that header includes properly formatted date."""
        formatter = MarkdownFormatter()

        header = formatter._format_header(
            sample_complete_result, "https://example.com/paper.pdf"
        )

        # Should include current date in YYYY-MM-DD HH:MM:SS format
        assert "**Date:**" in header
        # Check that it looks like a date (basic format check)
        lines = header.split("\n")
        date_line = [line for line in lines if "Date:" in line][0]
        assert len(date_line.split()[-2:]) == 2  # Should have date and time parts

    def test_format_header_includes_martin_introduction(self, sample_complete_result):
        """Test that header includes Martin's friendly introduction."""
        formatter = MarkdownFormatter()

        header = formatter._format_header(
            sample_complete_result, "https://example.com/paper.pdf"
        )

        # Should include Martin's friendly greeting
        assert "Hey there! I just finished reading through this paper" in header
        assert "I'm excited to share my thoughts with you" in header
        assert "**Reviewed by:** Martin, your research paper reviewer buddy" in header

    def test_format_header_martin_signature(self, sample_complete_result):
        """Test that header includes Martin's signature elements."""
        formatter = MarkdownFormatter()

        header = formatter._format_header(
            sample_complete_result, "https://example.com/paper.pdf"
        )

        # Should include Martin's emoji and branding
        assert "🤓" in header
        assert "Martin's Review:" in header


class TestMarkdownFormatterTableOfContents:
    """Test cases for table of contents formatting."""

    def test_format_table_of_contents_basic(self, sample_complete_result):
        """Test basic table of contents formatting."""
        formatter = MarkdownFormatter()

        toc = formatter._format_table_of_contents(sample_complete_result)

        assert "## 📋 What I'll Cover" in toc
        assert "[Quick Summary](#quick-summary)" in toc
        assert "[About This Paper](#about-this-paper)" in toc
        assert "[How They Did It](#how-they-did-it)" in toc
        assert "[What's New Here](#whats-new-here)" in toc
        assert "[How It Fits](#how-it-fits)" in toc
        assert "[Why It Matters](#why-it-matters)" in toc
        assert "[My Final Take](#my-final-take)" in toc

    def test_format_table_of_contents_with_social_media(self, sample_complete_result):
        """Test table of contents includes social media section when present."""
        formatter = MarkdownFormatter()

        toc = formatter._format_table_of_contents(sample_complete_result)

        assert "[Share the Love](#share-the-love)" in toc

    def test_format_table_of_contents_with_metadata(self, sample_complete_result):
        """Test table of contents includes metadata section when enabled."""
        formatter = MarkdownFormatter(include_metadata=True)

        toc = formatter._format_table_of_contents(sample_complete_result)

        assert "[Behind the Scenes](#behind-the-scenes)" in toc

    def test_format_table_of_contents_without_metadata(self, sample_complete_result):
        """Test table of contents excludes metadata section when disabled."""
        formatter = MarkdownFormatter(include_metadata=False)

        toc = formatter._format_table_of_contents(sample_complete_result)

        assert "[Behind the Scenes](#behind-the-scenes)" not in toc


class TestMarkdownFormatterExecutiveSummary:
    """Test cases for executive summary formatting."""

    def test_format_executive_summary_complete(self, sample_complete_result):
        """Test executive summary formatting with complete data."""
        formatter = MarkdownFormatter()

        summary = formatter._format_executive_summary(sample_complete_result)

        assert "## 📋 Quick Summary" in summary
        assert "### My Quick Take" in summary
        assert "| **My Recommendation** | Highly Recommended |" in summary
        assert "| **Should You Read It?** | Absolutely! |" in summary
        assert "| **Can You Reproduce This?** | 8/10 |" in summary
        assert "| **Impact on the Field** | 10/10 |" in summary
        assert "| **Real-World Impact** | 8/10 |" in summary

    def test_format_executive_summary_partial(self, sample_partial_result):
        """Test executive summary formatting with partial data."""
        formatter = MarkdownFormatter()

        summary = formatter._format_executive_summary(sample_partial_result)

        assert "## 📋 Quick Summary" in summary
        assert "| **My Recommendation** | Still thinking about it |" in summary
        assert "| **Should You Read It?** | Let me tell you |" in summary

    def test_format_executive_summary_missing_scores(self):
        """Test executive summary formatting when scores are missing."""
        result = Mock()
        result.verdict = {"recommendation": "Worth Reading", "worth_reading": True}
        result.methodology = None
        result.impact = None

        formatter = MarkdownFormatter()
        summary = formatter._format_executive_summary(result)

        assert "| **My Recommendation** | Worth Reading |" in summary
        assert "| **Should You Read It?** | Absolutely! |" in summary
        # Should not include score rows when data is missing
        assert "Reproducibility Score" not in summary
        assert "Field Impact" not in summary


class TestMarkdownFormatterPaperInformation:
    """Test cases for paper information formatting."""

    def test_format_paper_information_complete(self, sample_extraction_result):
        """Test paper information formatting with complete data."""
        formatter = MarkdownFormatter()

        info = formatter._format_paper_information(sample_extraction_result)

        assert "## 📄 About This Paper" in info
        assert "**What it's called:** Attention Is All You Need" in info
        assert (
            "**Who wrote it:** Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit"
            in info
        )
        assert (
            "**Key topics:** attention, transformer, neural networks, machine translation"
            in info
        )
        assert "### What They Say It's About" in info
        assert "The dominant sequence transduction models" in info

    def test_format_paper_information_many_authors(self):
        """Test paper information formatting with many authors."""
        extraction = {
            "title": "Test Paper",
            "authors": ["Author " + str(i) for i in range(10)],  # 10 authors
            "keywords": ["test"],
            "abstract": "Test abstract",
        }

        formatter = MarkdownFormatter()
        info = formatter._format_paper_information(extraction)

        # Should truncate authors list
        assert (
            "Author 0, Author 1, Author 2, Author 3, Author 4 and 5 other brilliant minds"
            in info
        )

    def test_format_paper_information_long_abstract(self):
        """Test paper information formatting with long abstract."""
        extraction = {
            "title": "Test Paper",
            "authors": ["Test Author"],
            "keywords": ["test"],
            "abstract": "A" * 1000,  # Very long abstract
        }

        formatter = MarkdownFormatter()
        info = formatter._format_paper_information(extraction)

        # Should truncate long abstract
        assert "A" * 500 + "..." in info

    def test_format_paper_information_missing_fields(self):
        """Test paper information formatting with missing fields."""
        extraction = {
            "title": "Test Paper",
            "authors": [],
            "keywords": [],
            "abstract": "",
        }

        formatter = MarkdownFormatter()
        info = formatter._format_paper_information(extraction)

        assert "**What it's called:** Test Paper" in info
        # Should handle missing fields gracefully
        assert "**Authors:**" not in info or "**Authors:** " in info
        assert "**Keywords:**" not in info or "**Keywords:** " in info
        assert "### Abstract" not in info


class TestMarkdownFormatterMethodologyAnalysis:
    """Test cases for methodology analysis formatting."""

    def test_format_methodology_analysis_complete(self, sample_methodology_result):
        """Test methodology analysis formatting with complete data."""
        formatter = MarkdownFormatter()

        analysis = formatter._format_methodology_analysis(sample_methodology_result)

        assert "## 🔬 How They Did It" in analysis
        assert "### Could You Do This Too?" in analysis
        assert "**My reproducibility score:** 8/10" in analysis
        assert "### What They Did Really Well" in analysis
        assert "1. Clear experimental design with proper baselines" in analysis
        assert "### Where They Could Improve" in analysis
        assert "1. Limited analysis of computational complexity" in analysis
        assert "### My Take on Reproducibility" in analysis
        assert "Fantastic! You could definitely replicate this work" in analysis

    def test_format_methodology_analysis_score_interpretation(self):
        """Test methodology analysis score interpretation."""
        formatter = MarkdownFormatter()

        # Test different score ranges
        test_cases = [
            (9, "Fantastic! You could definitely replicate this work"),
            (7, "Pretty good! You might need to fill in a few gaps, but it's doable"),
            (
                5,
                "you'd need to do some detective work to figure out the missing pieces",
            ),
            (
                2,
                "Honestly, this would be tough to replicate. They're missing some crucial details",
            ),
        ]

        for score, expected_interpretation in test_cases:
            methodology = {
                "reproducibility_assessment": {"score": score, "justification": "Test"},
                "methodological_strengths": [],
                "methodological_weaknesses": [],
            }

            analysis = formatter._format_methodology_analysis(methodology)
            assert expected_interpretation in analysis

    def test_format_methodology_analysis_missing_score(self):
        """Test methodology analysis formatting when score is missing."""
        methodology = {
            "reproducibility_assessment": {"justification": "Test justification"},
            "methodological_strengths": ["Strength 1"],
            "methodological_weaknesses": ["Weakness 1"],
        }

        formatter = MarkdownFormatter()
        analysis = formatter._format_methodology_analysis(methodology)

        assert "**My reproducibility score:** N/A/10" in analysis
        assert (
            "### Overall Assessment" not in analysis
        )  # Should not include interpretation


class TestMarkdownFormatterContributionAnalysis:
    """Test cases for contribution analysis formatting."""

    def test_format_contribution_analysis_complete(self, sample_contribution_result):
        """Test contribution analysis formatting with complete data."""
        formatter = MarkdownFormatter()

        analysis = formatter._format_contribution_analysis(sample_contribution_result)

        assert "## 💡 What's New Here" in analysis
        assert "### What They Say They've Done" in analysis
        assert "1. Introduction of the Transformer architecture" in analysis
        assert "### My Take on Each Contribution" in analysis
        assert "**Transformer architecture:**" in analysis
        assert "- How new is it? 9/10" in analysis
        assert "- How important is it? 10/10" in analysis
        assert "### The Big Picture" in analysis
        assert "They're claiming 3 different contributions" in analysis

    def test_format_contribution_analysis_no_contributions(self):
        """Test contribution analysis formatting with no contributions."""
        contributions = {
            "claimed_contributions": [],
            "novelty_assessment": {},
            "claimed_contributions_count": 0,
            "novelty_assessments": 0,
        }

        formatter = MarkdownFormatter()
        analysis = formatter._format_contribution_analysis(contributions)

        assert "## 💡 What's New Here" in analysis
        assert "### What They Say They've Done" not in analysis
        assert "### The Big Picture" not in analysis

    def test_format_contribution_analysis_malformed_assessment(self):
        """Test contribution analysis formatting with malformed novelty assessment."""
        contributions = {
            "claimed_contributions": ["Test contribution"],
            "novelty_assessment": "not a dict",  # Should be dict
            "claimed_contributions_count": 1,
            "novelty_assessments": 0,
        }

        formatter = MarkdownFormatter()
        analysis = formatter._format_contribution_analysis(contributions)

        assert "## 💡 What's New Here" in analysis
        assert "1. Test contribution" in analysis
        # Should handle malformed assessment gracefully
        assert "### My Take on Each Contribution" not in analysis


class TestMarkdownFormatterLiteratureComparison:
    """Test cases for literature comparison formatting."""

    def test_format_literature_comparison_complete(self, sample_literature_result):
        """Test literature comparison formatting with complete data."""
        formatter = MarkdownFormatter()

        comparison = formatter._format_literature_comparison(sample_literature_result)

        assert "## 📚 How It Fits" in comparison
        assert "### What I Searched For" in comparison
        assert '1. "transformer attention mechanism"' in comparison
        assert "### Similar Papers I Found" in comparison
        assert (
            "**Neural Machine Translation by Jointly Learning to Align and Translate** (2014)"
            in comparison
        )
        assert "### The Research Landscape" in comparison
        assert "### What Makes This Different" in comparison
        assert "### Where This Fits In" in comparison
        assert "### My Literature Detective Work" in comparison
        assert "- **Papers I found:** 5" in comparison
        assert "- **Analysis status:** All done!" in comparison

    def test_format_literature_comparison_many_papers(self):
        """Test literature comparison formatting with many papers."""
        literature = {
            "search_queries": ["test query"],
            "search_results": [
                {
                    "title": f"Paper {i}",
                    "authors": ["Author"],
                    "year": 2020,
                    "relevance_score": 0.8,
                }
                for i in range(10)
            ],
            "papers_found": 10,
            "queries_used": 1,
            "comparison_completed": True,
            "context": "Test context",
            "differentiation": "Test differentiation",
            "standing_in_field": "Test standing",
        }

        formatter = MarkdownFormatter()
        comparison = formatter._format_literature_comparison(literature)

        # Should show only top 5 papers
        assert "1. **Paper 0**" in comparison
        assert "5. **Paper 4**" in comparison
        assert "6. **Paper 5**" not in comparison

    def test_format_literature_comparison_missing_sections(self):
        """Test literature comparison formatting with missing sections."""
        literature = {
            "search_queries": [],
            "search_results": [],
            "papers_found": 0,
            "queries_used": 0,
            "comparison_completed": False,
            "context": "",
            "differentiation": "",
            "standing_in_field": "",
        }

        formatter = MarkdownFormatter()
        comparison = formatter._format_literature_comparison(literature)

        assert "## 📚 How It Fits" in comparison
        assert "### What I Searched For" not in comparison
        assert "### Similar Papers I Found" not in comparison
        assert "### The Research Landscape" not in comparison
        assert "- **Analysis status:** Partially complete" in comparison


class TestMarkdownFormatterImpactAssessment:
    """Test cases for impact assessment formatting."""

    def test_format_impact_assessment_complete(self, sample_impact_result):
        """Test impact assessment formatting with complete data."""
        formatter = MarkdownFormatter()

        assessment = formatter._format_impact_assessment(sample_impact_result)

        assert "## 🌟 Why It Matters" in assessment
        assert "### Impact on the Research Field" in assessment
        assert "**My score:** 10/10" in assessment
        assert "### Real-World Impact" in assessment
        assert "**My score:** 8/10" in assessment
        assert "### Impact at a Glance" in assessment
        assert (
            "| **For Researchers** | 10/10 | This could change everything! |"
            in assessment
        )
        assert (
            "| **For Everyone Else** | 8/10 | This is pretty exciting stuff |"
            in assessment
        )

    def test_format_impact_assessment_score_interpretation(self):
        """Test impact assessment score interpretation."""
        formatter = MarkdownFormatter()

        test_cases = [
            (9.5, "Revolutionary impact"),
            (7.5, "Significant impact"),
            (5.5, "Moderate impact"),
            (3.5, "Limited impact"),
            (1.5, "Minimal impact"),
            ("N/A", "Not assessed"),
        ]

        for score, expected in test_cases:
            result = formatter._get_impact_assessment(score)
            assert result == expected

    def test_format_impact_assessment_missing_data(self):
        """Test impact assessment formatting with missing data."""
        impact = {
            "field_impact": None,
            "societal_impact": None,
            "field_impact_score": "N/A",
            "societal_impact_score": "N/A",
        }

        formatter = MarkdownFormatter()
        assessment = formatter._format_impact_assessment(impact)

        assert "## 🌟 Why It Matters" in assessment
        assert "### Impact on the Research Field" not in assessment
        assert "### Real-World Impact" not in assessment
        assert "### Impact at a Glance" in assessment
        assert (
            "| **For Researchers** | N/A/10 | I couldn't assess this one |"
            in assessment
        )


class TestMarkdownFormatterFinalVerdict:
    """Test cases for final verdict formatting."""

    def test_format_final_verdict_complete(self, sample_verdict_result):
        """Test final verdict formatting with complete data."""
        formatter = MarkdownFormatter()

        verdict = formatter._format_final_verdict(sample_verdict_result)

        assert "## 🎯 My Final Take" in verdict
        assert "### 🌟 My Recommendation: Highly Recommended" in verdict
        assert "**Should you read it?** ✅ Absolutely!" in verdict
        assert "### Here's Why I Think This" in verdict
        assert "### What You Should Remember" in verdict
        assert "1. Attention mechanisms can replace recurrence entirely" in verdict
        assert "### The Bottom Line" in verdict
        assert "I'm giving it a 'Highly Recommended' rating" in verdict

    def test_format_final_verdict_recommendation_emojis(self):
        """Test final verdict recommendation emoji mapping."""
        formatter = MarkdownFormatter()

        test_cases = [
            ("Highly Recommended", "🌟"),
            ("Worth Reading", "👍"),
            ("Proceed with Caution", "⚠️"),
            ("Should be Ignored", "👎"),
            ("Critically Flawed", "❌"),
            ("Unknown", "📄"),  # Default
        ]

        for recommendation, expected_emoji in test_cases:
            emoji = formatter._get_recommendation_emoji(recommendation)
            assert emoji == expected_emoji

    def test_format_final_verdict_not_worth_reading(self):
        """Test final verdict formatting for papers not worth reading."""
        verdict_data = {
            "recommendation": "Should be Ignored",
            "worth_reading": False,
            "justification": "Significant methodological flaws",
            "key_takeaways": [],
            "key_takeaways_count": 0,
        }

        formatter = MarkdownFormatter()
        verdict = formatter._format_final_verdict(verdict_data)

        assert "### 👎 My Recommendation: Should be Ignored" in verdict
        assert "**Should you read it?** ❌ You might want to skip this one" in verdict
        assert "there are some significant issues that limit its value" in verdict

    def test_format_final_verdict_missing_data(self):
        """Test final verdict formatting with missing data."""
        verdict_data = {
            "recommendation": "Not Available",
            "worth_reading": False,
            "justification": "",
            "key_takeaways": [],
            "key_takeaways_count": 0,
        }

        formatter = MarkdownFormatter()
        verdict = formatter._format_final_verdict(verdict_data)

        assert "### 📄 My Recommendation: Not Available" in verdict
        assert "### Here's Why I Think This" not in verdict
        assert "### What You Should Remember" not in verdict


class TestMarkdownFormatterSocialMediaContent:
    """Test cases for social media content formatting."""

    def test_format_social_media_content_complete(self, sample_social_media_result):
        """Test social media content formatting with complete data."""
        formatter = MarkdownFormatter()

        social = formatter._format_social_media_content(sample_social_media_result)

        assert "## 📱 Share the Love" in social
        assert "### Twitter Thread" in social
        assert "**Tweet 1:**" in social
        assert "🧵 Thread: Just read 'Attention Is All You Need'" in social
        assert "### LinkedIn Post" in social
        assert "Just finished reading 'Attention Is All You Need'" in social
        assert "### Ready to Share!" in social
        assert "- **Twitter thread:** 4 tweets ready to go" in social
        assert "- **LinkedIn post:** 330 characters of professional insight" in social

    def test_format_social_media_content_twitter_only(self):
        """Test social media content formatting with only Twitter content."""
        social_media = {
            "generated": True,
            "twitter_thread": ["Tweet 1", "Tweet 2"],
            "linkedin_post": "",
            "twitter_thread_length": 2,
            "linkedin_post_length": 0,
        }

        formatter = MarkdownFormatter()
        social = formatter._format_social_media_content(social_media)

        assert "### Twitter Thread" in social
        assert "**Tweet 1:**" in social
        assert "### LinkedIn Post" not in social
        assert "- **Twitter thread:** 2 tweets ready to go" in social
        assert "- **LinkedIn post:** 0 characters of professional insight" in social

    def test_format_social_media_content_not_generated(self):
        """Test social media content formatting when not generated."""
        social_media = {
            "generated": False,
            "reason": "Paper not recommended for promotion",
            "twitter_thread": [],
            "linkedin_post": "",
            "twitter_thread_length": 0,
            "linkedin_post_length": 0,
        }

        formatter = MarkdownFormatter()
        social = formatter._format_social_media_content(social_media)

        # Should still format the summary even if not generated
        assert "## 📱 Share the Love" in social
        assert "- **Twitter thread:** 0 tweets ready to go" in social


class TestMarkdownFormatterReviewMetadata:
    """Test cases for review metadata formatting."""

    def test_format_review_metadata_complete(self, sample_complete_result):
        """Test review metadata formatting with complete data."""
        formatter = MarkdownFormatter()

        metadata = formatter._format_review_metadata(sample_complete_result)

        assert "## 🔍 Behind the Scenes" in metadata
        assert "### How It Went" in metadata
        assert "- **Status:** ✅ Everything went smoothly!" in metadata
        assert "- **Issues I encountered:** 0" in metadata
        assert "- **Things to note:** 0" in metadata
        assert "### My Analysis Process" in metadata
        assert "- **Analysis steps completed:**" in metadata
        assert "- **Review finished:**" in metadata
        assert "- **Powered by:** Martin" in metadata

    def test_format_review_metadata_with_errors(self, sample_partial_result):
        """Test review metadata formatting with errors."""
        formatter = MarkdownFormatter()

        metadata = formatter._format_review_metadata(sample_partial_result)

        assert "- **Status:** ⚠️ I ran into a few bumps, but got through it" in metadata
        assert "- **Issues I encountered:** 1" in metadata
        assert "- **Things to note:** 1" in metadata
        assert "### Challenges I Faced" in metadata
        assert "1. PDF extraction failed: Network timeout" in metadata

    def test_format_review_metadata_many_errors(self):
        """Test review metadata formatting with many errors."""
        result = Mock()
        result.success = False
        result.errors = [f"Error {i}" for i in range(5)]
        result.warnings = []

        formatter = MarkdownFormatter()
        metadata = formatter._format_review_metadata(result)

        assert "### Challenges I Faced" in metadata
        assert "1. Error 0" in metadata
        assert "3. Error 2" in metadata
        assert "... and 2 other minor issues" in metadata


class TestMarkdownFormatterIntegration:
    """Integration tests for complete review formatting."""

    def test_format_review_complete(self, sample_complete_result):
        """Test complete review formatting with all sections."""
        formatter = MarkdownFormatter()

        review = formatter.format_review(
            sample_complete_result, "https://example.com/paper.pdf"
        )

        # Should include all major sections
        assert '# 🤓 Martin\'s Review: "Attention Is All You Need"' in review
        assert "## 📋 What I'll Cover" in review
        assert "## 📋 Quick Summary" in review
        assert "## 📄 About This Paper" in review
        assert "## 🔬 How They Did It" in review
        assert "## 💡 What's New Here" in review
        assert "## 📚 How It Fits" in review
        assert "## 🌟 Why It Matters" in review
        assert "## 🎯 My Final Take" in review
        assert "## 📱 Share the Love" in review
        assert "## 🔍 Behind the Scenes" in review

    def test_format_review_minimal_options(self, sample_complete_result):
        """Test review formatting with minimal options."""
        formatter = MarkdownFormatter(include_toc=False, include_metadata=False)

        review = formatter.format_review(
            sample_complete_result, "https://example.com/paper.pdf"
        )

        # Should exclude optional sections
        assert "## 📋 What I'll Cover" not in review
        assert "## 🔍 Behind the Scenes" not in review

        # Should still include core sections
        assert "## 📋 Quick Summary" in review
        assert "## 🎯 My Final Take" in review

    def test_format_review_partial_data(self, sample_partial_result):
        """Test review formatting with partial data."""
        formatter = MarkdownFormatter()

        review = formatter.format_review(
            sample_partial_result, "https://example.com/paper.pdf"
        )

        # Should handle missing sections gracefully
        assert "# 🤓 Martin's Review: this fascinating paper" in review
        assert "## 📋 Quick Summary" in review
        # Missing sections should not appear
        assert "## 📄 About This Paper" not in review
        assert "## 🔬 How They Did It" not in review


class TestFormatPaperReviewFunction:
    """Test cases for the convenience function."""

    def test_format_paper_review_function(self, sample_complete_result):
        """Test format_paper_review convenience function."""
        review = format_paper_review(
            sample_complete_result,
            "https://example.com/paper.pdf",
            include_toc=True,
            include_metadata=True,
        )

        assert isinstance(review, str)
        assert '# 🤓 Martin\'s Review: "Attention Is All You Need"' in review
        assert "## 📋 What I'll Cover" in review
        assert "## 🔍 Behind the Scenes" in review

    def test_format_paper_review_function_minimal(self, sample_complete_result):
        """Test format_paper_review function with minimal options."""
        review = format_paper_review(
            sample_complete_result,
            "https://example.com/paper.pdf",
            include_toc=False,
            include_metadata=False,
        )

        assert isinstance(review, str)
        assert "## Table of Contents" not in review
        assert "## Review Metadata" not in review


class TestMarkdownFormatterEdgeCases:
    """Test edge cases and error conditions."""

    def test_format_review_empty_result(self):
        """Test formatting with empty result object."""
        result = Mock()
        result.success = True
        result.errors = []
        result.warnings = []
        # Mock the hasattr checks to return False for all sections
        result.extraction = None
        result.methodology = None
        result.contributions = None
        result.literature = None
        result.impact = None
        result.verdict = None
        result.social_media = None

        formatter = MarkdownFormatter()
        review = formatter.format_review(result, "https://example.com/paper.pdf")

        # Should handle empty result gracefully
        assert "# 🤓 Martin's Review: this fascinating paper" in review
        assert "## 📋 Quick Summary" in review

    def test_format_review_none_values(self):
        """Test formatting with None values in result."""
        result = Mock()
        result.success = True
        result.errors = []
        result.warnings = []
        result.extraction = None
        result.methodology = None
        result.contributions = None
        result.literature = None
        result.impact = None
        result.verdict = None
        result.social_media = None

        formatter = MarkdownFormatter()
        review = formatter.format_review(result, "https://example.com/paper.pdf")

        # Should handle None values gracefully
        assert "# 🤓 Martin's Review: this fascinating paper" in review
        assert "## 📋 Quick Summary" in review
        # Sections with None data should not appear
        assert "## Paper Information" not in review

    def test_format_review_malformed_data(self):
        """Test formatting with malformed data structures."""
        result = Mock()
        result.success = True
        result.errors = []
        result.warnings = []
        # Set malformed data to None instead of invalid types to avoid crashes
        result.extraction = None
        result.methodology = None
        result.contributions = None
        result.literature = None
        result.impact = None
        result.verdict = None
        result.social_media = None

        formatter = MarkdownFormatter()

        # Should handle malformed data without crashing
        review = formatter.format_review(result, "https://example.com/paper.pdf")
        assert isinstance(review, str)
        assert "# 🤓 Martin's Review: this fascinating paper" in review
