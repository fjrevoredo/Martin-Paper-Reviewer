"""
Integration validation tests for Martin.

These tests validate that Martin works end-to-end with real papers.
They are designed to be part of the regular test suite but can be
skipped in CI if API keys are not available.
"""

# Load environment variables from .env file FIRST
from dotenv import load_dotenv
load_dotenv()

import os
import pytest
import time
from typing import Dict, Any

# Mark all tests in this module as integration tests
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not os.getenv("OPENROUTER_API_KEY"),
        reason="OPENROUTER_API_KEY not available - skipping integration tests"
    )
]


class TestMartinIntegration:
    """Integration tests for Martin's end-to-end functionality."""
    
    @pytest.fixture(scope="class")
    def reviewer(self):
        """Create a PaperReviewer instance for testing."""
        # Ensure environment variables are loaded
        from dotenv import load_dotenv
        load_dotenv()
        
        from martin.paper_reviewer import PaperReviewer
        from martin.config import Config
        
        # Create a fresh config instance that will read the newly loaded env vars
        config = Config()
        
        # Configure DSPy
        config.setup_dspy_lm()
        
        # Create reviewer with minimal settings for speed
        return PaperReviewer(
            max_search_results=1,
            enable_social_media=False,
            verbose=False
        )
    
    def test_basic_paper_analysis(self, reviewer):
        """Test that Martin can analyze a well-known paper successfully."""
        # Use a short, well-known paper
        test_url = "https://arxiv.org/pdf/1706.03762.pdf"  # Attention Is All You Need
        
        start_time = time.time()
        result = reviewer.forward(test_url)
        analysis_time = time.time() - start_time
        
        # Validate result structure
        assert hasattr(result, '_store'), "Result should have _store attribute"
        
        store = result._store
        assert isinstance(store, dict), "Store should be a dictionary"
        assert store.get("success", False), f"Analysis should succeed. Errors: {store.get('errors', [])}"
        
        # Validate required components exist
        assert "pdf_url" in store
        assert "extraction" in store
        assert "methodology" in store
        assert "verdict" in store
        
        # Validate analysis completed in reasonable time (< 3 minutes, accounting for API rate limits)
        assert analysis_time < 180, f"Analysis took too long: {analysis_time:.1f}s"
        
        # Validate extraction results
        extraction = store["extraction"]
        assert isinstance(extraction, dict)
        assert extraction.get("title"), "Should extract paper title"
        assert extraction.get("authors"), "Should extract authors"
        
        # Validate methodology results
        methodology = store["methodology"]
        assert isinstance(methodology, dict)
        
        # Validate verdict results
        verdict = store["verdict"]
        assert isinstance(verdict, dict)
        assert verdict.get("recommendation"), "Should provide recommendation"
        
        print(f"✅ Integration test passed in {analysis_time:.1f}s")
    
    def test_paper_analysis_consistency(self, reviewer):
        """Test that Martin produces consistent results across multiple runs."""
        test_url = "https://arxiv.org/pdf/1706.03762.pdf"
        
        results = []
        for i in range(2):  # Run twice for consistency check
            result = reviewer.forward(test_url)
            
            assert hasattr(result, '_store'), f"Run {i+1}: Result should have _store attribute"
            store = result._store
            assert store.get("success", False), f"Run {i+1}: Analysis should succeed"
            
            # Extract key metrics for consistency comparison
            methodology = store.get("methodology", {})
            verdict = store.get("verdict", {})
            
            run_result = {
                "recommendation": verdict.get("recommendation"),
                "has_methodology": bool(methodology),
                "has_verdict": bool(verdict)
            }
            results.append(run_result)
        
        # Check consistency
        assert len(results) == 2, "Should have 2 results"
        
        # Recommendations should be consistent (or at least reasonable)
        rec1, rec2 = results[0]["recommendation"], results[1]["recommendation"]
        if rec1 and rec2:
            # Both should be positive recommendations for this well-known paper
            positive_recs = ["Highly Recommended", "Recommended", "Accept", "Strong Accept"]
            assert rec1 in positive_recs, f"First recommendation should be positive: {rec1}"
            assert rec2 in positive_recs, f"Second recommendation should be positive: {rec2}"
        
        # Structure should be consistent
        assert results[0]["has_methodology"] == results[1]["has_methodology"]
        assert results[0]["has_verdict"] == results[1]["has_verdict"]
        
        print("✅ Consistency test passed")
    
    def test_error_handling(self, reviewer):
        """Test that Martin handles invalid inputs gracefully."""
        # Test with invalid URL
        invalid_url = "https://example.com/nonexistent.pdf"
        
        # Martin currently fails fast with clear error messages for invalid URLs
        # This is the expected behavior - it should raise an exception with a helpful message
        with pytest.raises(Exception) as exc_info:
            reviewer.forward(invalid_url)
        
        # Verify the error message is helpful and user-friendly
        error_message = str(exc_info.value)
        assert "download" in error_message.lower() or "404" in error_message, \
            f"Error message should mention download issue: {error_message}"
        
        # Verify it's a user-friendly message (contains Martin's personality)
        assert any(phrase in error_message for phrase in ["😔", "tried my best", "server seems"]), \
            f"Error message should be user-friendly: {error_message}"
        
        print("✅ Error handling test passed")


@pytest.mark.slow
@pytest.mark.integration
class TestMartinBenchmark:
    """Benchmark tests for Martin's performance and accuracy."""
    
    @pytest.fixture(scope="class")
    def benchmark_papers(self):
        """Test papers for benchmarking."""
        return [
            {
                "url": "https://arxiv.org/pdf/1706.03762.pdf",
                "name": "Attention Is All You Need",
                "expected_positive": True,  # Should get positive recommendation
                "max_time": 180  # Should complete within 3 minutes (accounting for API rate limits)
            }
        ]
    
    @pytest.fixture(scope="class")
    def reviewer(self):
        """Create a PaperReviewer instance for benchmarking."""
        # Ensure environment variables are loaded
        from dotenv import load_dotenv
        load_dotenv()
        
        from martin.paper_reviewer import PaperReviewer
        from martin.config import Config
        
        # Create a fresh config instance that will read the newly loaded env vars
        config = Config()
        config.setup_dspy_lm()
        
        return PaperReviewer(
            max_search_results=1,
            enable_social_media=False,
            verbose=False
        )
    
    def test_benchmark_paper_analysis(self, reviewer, benchmark_papers):
        """Benchmark Martin's analysis of known papers."""
        results = []
        
        for paper in benchmark_papers:
            print(f"\n📄 Benchmarking: {paper['name']}")
            
            start_time = time.time()
            result = reviewer.forward(paper["url"])
            analysis_time = time.time() - start_time
            
            # Validate basic success
            assert hasattr(result, '_store'), f"Paper {paper['name']}: Should have _store"
            store = result._store
            
            benchmark_result = {
                "paper": paper["name"],
                "success": store.get("success", False),
                "analysis_time": analysis_time,
                "errors": store.get("errors", [])
            }
            
            if benchmark_result["success"]:
                # Extract metrics
                verdict = store.get("verdict", {})
                recommendation = verdict.get("recommendation")
                
                benchmark_result["recommendation"] = recommendation
                
                # Validate expectations
                if paper["expected_positive"] and recommendation:
                    positive_recs = ["Highly Recommended", "Recommended", "Accept", "Strong Accept"]
                    assert recommendation in positive_recs, \
                        f"Expected positive recommendation for {paper['name']}, got: {recommendation}"
                
                # Validate performance
                assert analysis_time < paper["max_time"], \
                    f"Analysis of {paper['name']} took too long: {analysis_time:.1f}s > {paper['max_time']}s"
                
                print(f"   ✅ Success in {analysis_time:.1f}s - {recommendation}")
            else:
                print(f"   ❌ Failed: {benchmark_result['errors']}")
                # Don't fail the test immediately - collect all results
            
            results.append(benchmark_result)
        
        # Analyze overall benchmark results
        successful = [r for r in results if r["success"]]
        success_rate = len(successful) / len(results) if results else 0
        
        print(f"\n📊 Benchmark Results:")
        print(f"   Success Rate: {success_rate:.1%} ({len(successful)}/{len(results)})")
        
        if successful:
            avg_time = sum(r["analysis_time"] for r in successful) / len(successful)
            print(f"   Average Time: {avg_time:.1f}s")
        
        # Benchmark should have reasonable success rate
        assert success_rate >= 0.5, f"Benchmark success rate too low: {success_rate:.1%}"
        
        print("✅ Benchmark test passed")


# Utility functions for manual testing
def run_quick_validation():
    """Quick validation function that can be called manually."""
    try:
        from martin.paper_reviewer import PaperReviewer
        from martin.config import config
        
        config.setup_dspy_lm()
        reviewer = PaperReviewer(max_search_results=1, enable_social_media=False, verbose=False)
        
        result = reviewer.forward("https://arxiv.org/pdf/1706.03762.pdf")
        
        if hasattr(result, '_store') and result._store.get("success", False):
            print("✅ Quick validation passed")
            return True
        else:
            print("❌ Quick validation failed")
            return False
    except Exception as e:
        print(f"❌ Quick validation error: {e}")
        return False


if __name__ == "__main__":
    # Allow running this file directly for quick testing
    print("🔍 Running quick validation...")
    success = run_quick_validation()
    exit(0 if success else 1)