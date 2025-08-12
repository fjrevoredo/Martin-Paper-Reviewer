"""
Main PaperReviewer DSPy Module

Orchestrates the complete research paper review pipeline using DSPy signatures.
Provides a comprehensive analysis from PDF extraction to final recommendation.
"""

import traceback
from typing import Any, Dict, Optional

import dspy

from .models.paper_text import PaperText
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
from .tools.pdf_extractor import PDFTextExtractor
from .tools.real_academic_search import RealAcademicSearch


class PaperReviewer(dspy.Module):
    """
    Main DSPy module for comprehensive research paper review.

    This module orchestrates the complete analysis pipeline:
    1. PDF text extraction and parsing
    2. Initial bibliographic extraction
    3. Methodology analysis with reproducibility scoring
    4. Contribution identification and evaluation
    5. Literature search and comparison (RAG pattern)
    6. Impact assessment (field and societal)
    7. Final verdict with recommendation
    8. Social media content generation (for valuable papers)
    """

    def __init__(
        self,
        max_search_results: int = 5,
        enable_social_media: bool = True,
        continue_on_error: bool = False,
        verbose: bool = False,
    ):
        """
        Initialize the PaperReviewer module.

        Args:
            max_search_results: Maximum number of papers to retrieve for literature comparison
            enable_social_media: Whether to generate social media content for recommended papers
            continue_on_error: Whether to continue analysis if individual steps fail
            verbose: Whether to show detailed explanations of what Martin is doing
        """
        super().__init__()

        # Configuration
        self.max_search_results = max_search_results
        self.enable_social_media = enable_social_media
        self.continue_on_error = continue_on_error
        self.verbose = verbose

        # Initialize external tools
        self.pdf_extractor = PDFTextExtractor()
        self.search_engine = RealAcademicSearch(max_results=max_search_results)

        # Initialize DSPy signature modules
        self._initialize_signatures()

    def _verbose_print(self, message: str):
        """Print verbose messages when verbose mode is enabled."""
        if self.verbose:
            print(f"   💭 {message}")

    def _initialize_signatures(self):
        """Initialize all DSPy signature modules."""

        # Core analysis signatures
        self.extraction = dspy.Predict(InitialExtraction)
        self.methodology = dspy.ChainOfThought(MethodologyAnalysis)
        self.contribution = dspy.ChainOfThought(ContributionAnalysis)

        # Literature comparison (RAG pattern)
        self.query_generator = dspy.Predict(GenerateSearchQueries)
        self.comparison = dspy.ChainOfThought(LiteratureComparison)

        # Final synthesis
        self.impact = dspy.ChainOfThought(ImpactAssessment)
        self.verdict = dspy.ChainOfThought(FinalVerdict)
        self.socials = dspy.Predict(SocialMediaPromotion)

    def forward(self, pdf_url: str) -> dspy.Prediction:
        """
        Execute the complete paper review pipeline.

        Args:
            pdf_url: URL to the PDF research paper

        Returns:
            dspy.Prediction containing complete analysis results
        """
        results = {"pdf_url": pdf_url, "success": True, "errors": [], "warnings": []}

        try:
            # Step 1: PDF Text Extraction
            print("📄 Hey! I'm grabbing that paper for you...")
            self._verbose_print(
                "I'm downloading the PDF and extracting all the text so I can read through it properly."
            )
            paper_text = self._extract_pdf_content(pdf_url, results)
            if not paper_text:
                return dspy.Prediction(**results)

            # Step 2: Initial Extraction
            print("🔍 Now I'm diving into the details - this looks interesting!")
            self._verbose_print(
                "I'm pulling out the key info like the title, authors, and abstract to get oriented."
            )
            extraction_result = self._perform_initial_extraction(paper_text, results)

            # Step 3: Methodology Analysis
            print("🔬 Let me check out how they did their research...")
            self._verbose_print(
                "I'm examining their methods to see if they're solid and if other researchers could reproduce this work."
            )
            methodology_result = self._analyze_methodology(paper_text, results)

            # Step 4: Contribution Analysis
            print("💡 Time to see what new ideas they're bringing to the table!")
            self._verbose_print(
                "I'm identifying what's genuinely new here and how it builds on existing knowledge."
            )
            contribution_result = self._analyze_contributions(paper_text, results)

            # Step 5: Literature Search and Comparison (RAG)
            print("📚 I'm comparing this with other papers I know about...")
            self._verbose_print(
                "I'm searching through academic databases to see how this fits with related research."
            )
            literature_result = self._perform_literature_comparison(
                extraction_result, contribution_result, results
            )

            # Step 6: Impact Assessment
            print("🌟 Now I'm thinking about how this could change things...")
            self._verbose_print(
                "I'm evaluating whether this could make waves in the field or have broader implications."
            )
            impact_result = self._assess_impact(
                methodology_result, contribution_result, literature_result, results
            )

            # Step 7: Final Verdict
            print("🤔 Almost done! Just putting together my final thoughts...")
            self._verbose_print(
                "I'm weighing everything I've learned to give you my honest recommendation."
            )
            verdict_result = self._generate_final_verdict(
                extraction_result,
                methodology_result,
                contribution_result,
                literature_result,
                impact_result,
                results,
            )

            # Step 8: Social Media Content (conditional)
            if self.enable_social_media and verdict_result:
                print("📱 This paper's worth sharing - let me write something catchy!")
                self._verbose_print(
                    "Since this is a solid paper, I'm crafting some social media posts to help spread the word."
                )
                self._generate_social_content(
                    extraction_result, verdict_result, impact_result, results
                )

            print(
                "🎉 All finished! Here's what I discovered about this fascinating research..."
            )

        except Exception as e:
            error_msg = f"😅 I ran into a critical issue during analysis: {str(e)}"
            results["errors"].append(error_msg)
            results["success"] = False

            if not self.continue_on_error:
                raise

            print(f"😅 Oops! I ran into a problem while analyzing this paper: {str(e)}")
            print(
                "   Don't worry though - this happens sometimes with complex research papers!"
            )

        return dspy.Prediction(**results)

    def _extract_pdf_content(self, pdf_url: str, results: Dict) -> Optional[PaperText]:
        """Extract and parse PDF content."""
        try:
            paper_text = self.pdf_extractor.extract_from_url(pdf_url)
            results["paper_text"] = {
                "full_text_length": len(paper_text.full_text),
                "sections_found": paper_text.get_section_summary(),
            }
            return paper_text

        except Exception as e:
            error_msg = f"📄 I had trouble getting the PDF content: {str(e)}"
            results["errors"].append(error_msg)

            if not self.continue_on_error:
                raise

            print(
                f"😅 I had trouble getting that paper - the server might be busy or the link might need checking. ({str(e)})"
            )
            return None

    def _perform_initial_extraction(
        self, paper_text: PaperText, results: Dict
    ) -> Optional[Any]:
        """Perform initial bibliographic extraction."""
        try:
            result = self.extraction(paper_text=paper_text.full_text)

            results["extraction"] = {
                "title": result.title,
                "authors": result.authors,
                "keywords": result.keywords,
                "abstract": result.abstract,
                "abstract_length": len(result.abstract),
            }

            return result

        except Exception as e:
            error_msg = f"🔍 I struggled with the initial paper analysis: {str(e)}"
            results["errors"].append(error_msg)

            if not self.continue_on_error:
                raise

            print(
                f"🤔 I'm having trouble parsing the basic info from this paper. The formatting might be unusual. ({str(e)})"
            )
            return None

    def _analyze_methodology(
        self, paper_text: PaperText, results: Dict
    ) -> Optional[Any]:
        """Analyze research methodology."""
        try:
            if not paper_text.methodology:
                results["warnings"].append("No methodology section found")
                return None

            result = self.methodology(methodology_section=paper_text.methodology)

            results["methodology"] = {
                "methodological_strengths": result.methodological_strengths,
                "methodological_weaknesses": result.methodological_weaknesses,
                "reproducibility_assessment": result.reproducibility_assessment,
                "strengths_count": len(result.methodological_strengths),
                "weaknesses_count": len(result.methodological_weaknesses),
                "reproducibility_score": result.reproducibility_assessment.get(
                    "score", 0
                ),
            }

            return result

        except Exception as e:
            error_msg = f"🔬 I had trouble analyzing the methodology section: {str(e)}"
            results["errors"].append(error_msg)

            if not self.continue_on_error:
                raise

            print(
                f"🔬 I'm struggling to analyze the methodology section - it might be written in an unusual way. ({str(e)})"
            )
            return None

    def _analyze_contributions(
        self, paper_text: PaperText, results: Dict
    ) -> Optional[Any]:
        """Analyze paper contributions."""
        try:
            if not paper_text.introduction or not paper_text.conclusion:
                results["warnings"].append(
                    "Missing introduction or conclusion sections"
                )
                # Use available content
                intro = paper_text.introduction or paper_text.abstract
                concl = paper_text.conclusion or paper_text.abstract
            else:
                intro = paper_text.introduction
                concl = paper_text.conclusion

            result = self.contribution(introduction=intro, conclusion=concl)

            results["contributions"] = {
                "claimed_contributions": result.claimed_contributions,
                "novelty_assessment": result.novelty_assessment,
                "claimed_contributions_count": len(result.claimed_contributions),
                "novelty_assessments": (
                    len(result.novelty_assessment)
                    if isinstance(result.novelty_assessment, dict)
                    else 0
                ),
            }

            return result

        except Exception as e:
            error_msg = f"💡 I struggled to identify the key contributions: {str(e)}"
            results["errors"].append(error_msg)

            if not self.continue_on_error:
                raise

            print(
                f"💡 I'm having trouble identifying the key contributions - the paper structure might be non-standard. ({str(e)})"
            )
            return None

    def _perform_literature_comparison(
        self, extraction_result: Any, contribution_result: Any, results: Dict
    ) -> Optional[Any]:
        """Perform literature search and comparison using RAG pattern."""
        try:
            if not extraction_result:
                results["warnings"].append(
                    "Skipping literature comparison - no extraction results"
                )
                return None

            # Generate search queries
            self._verbose_print(
                "First, I'm creating some smart search queries based on the paper's content."
            )
            query_result = self.query_generator(
                title=extraction_result.title, abstract=extraction_result.abstract
            )

            # Perform academic search
            self._verbose_print(
                f"Now I'm searching academic databases with {len(query_result.search_queries[:3])} different queries."
            )
            all_search_results = []
            for query in query_result.search_queries[:3]:  # Limit to top 3 queries
                try:
                    self._verbose_print(f"Searching for: '{query}'")
                    search_results = self.search_engine.search(query)
                    all_search_results.extend(search_results)
                except Exception as e:
                    results["warnings"].append(
                        f"🔍 Had trouble with one search query '{query}', but I'll keep looking: {str(e)}"
                    )

            # Remove duplicates and limit results
            self._verbose_print(
                "Filtering out duplicates and selecting the most relevant papers."
            )
            unique_results = []
            seen_titles = set()
            for result in all_search_results:
                if result.title not in seen_titles:
                    unique_results.append(result)
                    seen_titles.add(result.title)
                    if len(unique_results) >= self.max_search_results:
                        break

            if not unique_results:
                results["warnings"].append("No literature found for comparison")
                return None

            # Convert to dict format for signature
            search_results_dict = []
            for result in unique_results:
                search_results_dict.append(
                    {
                        "title": result.title,
                        "authors": result.authors,
                        "abstract": result.abstract,
                        "year": result.year,
                        "venue": result.venue,
                        "citation_count": result.citation_count,
                        "relevance_score": result.relevance_score,
                    }
                )

            # Perform literature comparison
            if contribution_result and contribution_result.claimed_contributions:
                comparison_result = self.comparison(
                    claimed_contributions=contribution_result.claimed_contributions,
                    search_results=search_results_dict,
                )

                results["literature"] = {
                    "context": comparison_result.context,
                    "differentiation": comparison_result.differentiation,
                    "standing_in_field": comparison_result.standing_in_field,
                    "search_queries": query_result.search_queries,
                    "search_results": search_results_dict,
                    "papers_found": len(unique_results),
                    "queries_used": len(query_result.search_queries),
                    "comparison_completed": True,
                }

                return comparison_result
            else:
                results["warnings"].append(
                    "No contributions found for literature comparison"
                )
                return None

        except Exception as e:
            error_msg = f"📚 I couldn't complete the literature comparison: {str(e)}"
            results["errors"].append(error_msg)

            if not self.continue_on_error:
                raise

            print(
                f"📚 I couldn't complete the literature comparison - the academic search might be having issues. ({str(e)})"
            )
            return None

    def _assess_impact(
        self,
        methodology_result: Any,
        contribution_result: Any,
        literature_result: Any,
        results: Dict,
    ) -> Optional[Any]:
        """Assess potential impact of the research."""
        try:
            # Compile analysis summary
            analysis_summary = {}

            if methodology_result:
                analysis_summary.update(
                    {
                        "methodological_strengths": methodology_result.methodological_strengths,
                        "methodological_weaknesses": methodology_result.methodological_weaknesses,
                        "reproducibility_assessment": methodology_result.reproducibility_assessment,
                    }
                )

            if contribution_result:
                analysis_summary.update(
                    {
                        "claimed_contributions": contribution_result.claimed_contributions,
                        "novelty_assessment": contribution_result.novelty_assessment,
                    }
                )

            # Literature comparison summary
            literature_comparison = {}
            if literature_result:
                literature_comparison = {
                    "context": literature_result.context,
                    "differentiation": literature_result.differentiation,
                    "standing_in_field": literature_result.standing_in_field,
                }

            if not analysis_summary:
                results["warnings"].append("Insufficient data for impact assessment")
                return None

            impact_result = self.impact(
                paper_analysis_summary=analysis_summary,
                literature_comparison=literature_comparison,
            )

            results["impact"] = {
                "field_impact": impact_result.field_impact,
                "societal_impact": impact_result.societal_impact,
                "field_impact_score": impact_result.field_impact.get("impact_score", 0),
                "societal_impact_score": impact_result.societal_impact.get(
                    "impact_score", 0
                ),
            }

            return impact_result

        except Exception as e:
            error_msg = f"🌟 I had trouble assessing the potential impact: {str(e)}"
            results["errors"].append(error_msg)

            if not self.continue_on_error:
                raise

            print(
                f"🌟 I'm having trouble assessing the potential impact - I might need more context about the field. ({str(e)})"
            )
            return None

    def _generate_final_verdict(
        self,
        extraction_result: Any,
        methodology_result: Any,
        contribution_result: Any,
        literature_result: Any,
        impact_result: Any,
        results: Dict,
    ) -> Optional[Any]:
        """Generate final verdict and recommendation."""
        try:
            # Compile complete analysis
            full_analysis = {}

            if extraction_result:
                full_analysis["title"] = extraction_result.title
                full_analysis["authors"] = extraction_result.authors
                full_analysis["keywords"] = extraction_result.keywords

            if methodology_result:
                full_analysis["methodology"] = {
                    "strengths": methodology_result.methodological_strengths,
                    "weaknesses": methodology_result.methodological_weaknesses,
                    "reproducibility": methodology_result.reproducibility_assessment,
                }

            if contribution_result:
                full_analysis["contributions"] = {
                    "claimed": contribution_result.claimed_contributions,
                    "novelty": contribution_result.novelty_assessment,
                }

            if literature_result:
                full_analysis["literature"] = {
                    "context": literature_result.context,
                    "differentiation": literature_result.differentiation,
                    "standing": literature_result.standing_in_field,
                }

            if impact_result:
                full_analysis["impact"] = {
                    "field": impact_result.field_impact,
                    "societal": impact_result.societal_impact,
                }

            if not full_analysis:
                results["warnings"].append("Insufficient data for final verdict")
                return None

            self._verbose_print(
                "I'm weighing all the evidence: methodology quality, novelty, literature fit, and potential impact."
            )
            verdict_result = self.verdict(full_analysis=full_analysis)

            results["verdict"] = {
                "recommendation": verdict_result.recommendation,
                "justification": verdict_result.justification,
                "worth_reading": verdict_result.worth_reading_verdict,
                "key_takeaways": verdict_result.key_takeaways,
                "key_takeaways_count": len(verdict_result.key_takeaways),
            }

            return verdict_result

        except Exception as e:
            error_msg = f"🤔 I struggled to put together my final thoughts: {str(e)}"
            results["errors"].append(error_msg)

            if not self.continue_on_error:
                raise

            print(
                f"🤔 I'm struggling to put together my final thoughts - there might be conflicting information in the analysis. ({str(e)})"
            )
            return None

    def _generate_social_content(
        self,
        extraction_result: Any,
        verdict_result: Any,
        impact_result: Any,
        results: Dict,
    ):
        """Generate social media content for recommended papers."""
        try:
            # Only generate for recommended papers
            if not verdict_result or verdict_result.recommendation not in [
                "Highly Recommended",
                "Worth Reading",
            ]:
                results["social_media"] = {
                    "generated": False,
                    "reason": "Paper not recommended for promotion",
                }
                return

            if not extraction_result or not impact_result:
                results["warnings"].append(
                    "Insufficient data for social media generation"
                )
                return

            social_result = self.socials(
                title=extraction_result.title,
                key_takeaways=verdict_result.key_takeaways,
                field_impact=impact_result.field_impact,
            )

            results["social_media"] = {
                "generated": True,
                "twitter_thread": social_result.twitter_thread,
                "linkedin_post": social_result.linkedin_post,
                "twitter_thread_length": len(social_result.twitter_thread),
                "linkedin_post_length": len(social_result.linkedin_post),
            }

        except Exception as e:
            error_msg = f"📱 I couldn't create the social media content: {str(e)}"
            results["errors"].append(error_msg)

            if not self.continue_on_error:
                raise

            print(
                f"📱 I couldn't create the social media content, but don't worry - the main review is still solid! ({str(e)})"
            )

    def review(self, pdf_url: str) -> dspy.Prediction:
        """
        Convenience method for reviewing a paper.

        Args:
            pdf_url: URL to the PDF research paper

        Returns:
            Complete review results
        """
        return self.forward(pdf_url)
