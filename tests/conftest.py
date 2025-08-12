"""
Shared pytest fixtures and configuration for Martin tests.

Provides common test data, mock objects, and utilities used across multiple test modules.
"""

from typing import Any, Dict, List
from unittest.mock import Mock

import dspy
import pytest

from martin.models.paper_text import PaperText


@pytest.fixture
def sample_paper_text():
    """Sample paper text content for testing."""
    return {
        "full_text": """
        Title: Attention Is All You Need
        
        Abstract
        The dominant sequence transduction models are based on complex recurrent or 
        convolutional neural networks that include an encoder and a decoder. The best 
        performing models also connect the encoder and decoder through an attention 
        mechanism. We propose a new simple network architecture, the Transformer, 
        based solely on attention mechanisms, dispensing with recurrence and convolutions 
        entirely.
        
        1 Introduction
        Recurrent neural networks, long short-term memory and gated recurrent neural 
        networks in particular, have been firmly established as state of the art approaches 
        in sequence modeling and transduction problems such as language modeling and 
        machine translation.
        
        2 Background
        The goal of reducing sequential computation also forms the foundation of the 
        Extended Neural GPU, ByteNet and ConvS2S, all of which use convolutional neural 
        networks as basic building block.
        
        3 Model Architecture
        Most competitive neural sequence transduction models have an encoder-decoder 
        structure. Here, the encoder maps an input sequence of symbol representations 
        to a sequence of continuous representations.
        
        4 Experiments
        We conducted experiments on two machine translation tasks. On the WMT 2014 
        English-to-German translation task, the big transformer model achieves 28.4 BLEU.
        
        5 Results
        Table 1 summarizes our results on English-to-German and English-to-French 
        newstest2014 tests. Our model achieves 28.4 BLEU on the English-to-German test.
        
        6 Conclusion
        In this work, we presented the Transformer, the first sequence transduction 
        model based entirely on attention, replacing the recurrent layers most commonly 
        used in encoder-decoder architectures with multi-headed self-attention.
        
        References
        [1] Dzmitry Bahdanau, Kyunghyun Cho, and Yoshua Bengio. Neural machine translation 
        by jointly learning to align and translate. arXiv preprint arXiv:1409.0473, 2014.
        """,
        "abstract": """The dominant sequence transduction models are based on complex recurrent or 
        convolutional neural networks that include an encoder and a decoder. The best 
        performing models also connect the encoder and decoder through an attention 
        mechanism. We propose a new simple network architecture, the Transformer, 
        based solely on attention mechanisms, dispensing with recurrence and convolutions 
        entirely.""",
        "introduction": """Recurrent neural networks, long short-term memory and gated recurrent neural 
        networks in particular, have been firmly established as state of the art approaches 
        in sequence modeling and transduction problems such as language modeling and 
        machine translation.""",
        "methodology": """Most competitive neural sequence transduction models have an encoder-decoder 
        structure. Here, the encoder maps an input sequence of symbol representations 
        to a sequence of continuous representations.""",
        "results": """Table 1 summarizes our results on English-to-German and English-to-French 
        newstest2014 tests. Our model achieves 28.4 BLEU on the English-to-German test.""",
        "conclusion": """In this work, we presented the Transformer, the first sequence transduction 
        model based entirely on attention, replacing the recurrent layers most commonly 
        used in encoder-decoder architectures with multi-headed self-attention.""",
        "references": """[1] Dzmitry Bahdanau, Kyunghyun Cho, and Yoshua Bengio. Neural machine translation 
        by jointly learning to align and translate. arXiv preprint arXiv:1409.0473, 2014.""",
    }


@pytest.fixture
def sample_paper_text_model(sample_paper_text):
    """Sample PaperText model instance for testing."""
    return PaperText(**sample_paper_text)


@pytest.fixture
def sample_extraction_result():
    """Sample extraction result for testing."""
    return {
        "title": "Attention Is All You Need",
        "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar", "Jakob Uszkoreit"],
        "keywords": [
            "attention",
            "transformer",
            "neural networks",
            "machine translation",
        ],
        "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...",
        "abstract_length": 245,
    }


@pytest.fixture
def sample_methodology_result():
    """Sample methodology analysis result for testing."""
    return {
        "methodological_strengths": [
            "Clear experimental design with proper baselines",
            "Comprehensive evaluation on multiple datasets",
            "Detailed ablation studies",
        ],
        "methodological_weaknesses": [
            "Limited analysis of computational complexity",
            "Insufficient discussion of failure cases",
        ],
        "reproducibility_assessment": {
            "score": 8,
            "justification": "Code and data are available, experimental setup is well documented",
        },
        "strengths_count": 3,
        "weaknesses_count": 2,
        "reproducibility_score": 8,
    }


@pytest.fixture
def sample_contribution_result():
    """Sample contribution analysis result for testing."""
    return {
        "claimed_contributions": [
            "Introduction of the Transformer architecture",
            "Elimination of recurrence in sequence modeling",
            "State-of-the-art results on machine translation",
        ],
        "novelty_assessment": {
            "Transformer architecture": {
                "novelty_score": 9,
                "significance_score": 10,
                "justification": "Revolutionary architecture that changed the field",
            },
            "Attention-only approach": {
                "novelty_score": 8,
                "significance_score": 9,
                "justification": "Novel approach to sequence modeling",
            },
        },
        "claimed_contributions_count": 3,
        "novelty_assessments": 2,
    }


@pytest.fixture
def sample_literature_result():
    """Sample literature comparison result for testing."""
    return {
        "context": "This work builds on previous attention mechanisms but eliminates recurrence entirely",
        "differentiation": "Unlike previous models, the Transformer uses only attention mechanisms",
        "standing_in_field": "This work represents a significant advancement in sequence modeling",
        "search_queries": [
            "transformer attention mechanism",
            "sequence to sequence models",
        ],
        "search_results": [
            {
                "title": "Neural Machine Translation by Jointly Learning to Align and Translate",
                "authors": ["Dzmitry Bahdanau", "Kyunghyun Cho"],
                "year": 2014,
                "relevance_score": 0.85,
            }
        ],
        "papers_found": 5,
        "queries_used": 2,
        "comparison_completed": True,
    }


@pytest.fixture
def sample_impact_result():
    """Sample impact assessment result for testing."""
    return {
        "field_impact": {
            "impact_score": 10,
            "reasoning": "Revolutionary impact on natural language processing and machine learning",
            "specific_areas": [
                "Machine Translation",
                "Language Modeling",
                "Computer Vision",
            ],
        },
        "societal_impact": {
            "impact_score": 8,
            "reasoning": "Enabled significant improvements in language technologies",
            "application_areas": [
                "Translation Services",
                "Search Engines",
                "Virtual Assistants",
            ],
        },
        "field_impact_score": 10,
        "societal_impact_score": 8,
    }


@pytest.fixture
def sample_verdict_result():
    """Sample final verdict result for testing."""
    return {
        "recommendation": "Highly Recommended",
        "justification": "Groundbreaking work that fundamentally changed sequence modeling",
        "worth_reading": True,
        "key_takeaways": [
            "Attention mechanisms can replace recurrence entirely",
            "Transformer architecture enables better parallelization",
            "Self-attention provides interpretable attention patterns",
        ],
        "key_takeaways_count": 3,
    }


@pytest.fixture
def sample_social_media_result():
    """Sample social media content result for testing."""
    return {
        "generated": True,
        "twitter_thread": [
            "🧵 Thread: Just read 'Attention Is All You Need' - the paper that changed everything! 1/4",
            "💡 Key insight: You don't need recurrence for sequence modeling. Pure attention is enough! 2/4",
            "🚀 The Transformer architecture enables much better parallelization than RNNs 3/4",
            "📊 Results: SOTA on machine translation with faster training. A true game-changer! 4/4",
        ],
        "linkedin_post": "Just finished reading 'Attention Is All You Need' by Vaswani et al. This groundbreaking paper introduced the Transformer architecture that revolutionized NLP. Key takeaway: attention mechanisms alone can outperform recurrent networks while being much more parallelizable. A must-read for anyone in ML/AI! #MachineLearning #NLP #AI",
        "twitter_thread_length": 4,
        "linkedin_post_length": 387,
    }


@pytest.fixture
def sample_complete_result(
    sample_extraction_result,
    sample_methodology_result,
    sample_contribution_result,
    sample_literature_result,
    sample_impact_result,
    sample_verdict_result,
    sample_social_media_result,
):
    """Complete sample result combining all analysis components."""
    return Mock(
        pdf_url="https://arxiv.org/pdf/1706.03762.pdf",
        success=True,
        errors=[],
        warnings=[],
        extraction=sample_extraction_result,
        methodology=sample_methodology_result,
        contributions=sample_contribution_result,
        literature=sample_literature_result,
        impact=sample_impact_result,
        verdict=sample_verdict_result,
        social_media=sample_social_media_result,
    )


@pytest.fixture
def sample_partial_result():
    """Sample result with missing components for testing error handling."""
    return Mock(
        pdf_url="https://arxiv.org/pdf/example.pdf",
        success=False,
        errors=["PDF extraction failed: Network timeout"],
        warnings=["No methodology section found"],
        extraction=None,
        methodology=None,
        contributions=None,
        literature=None,
        impact=None,
        verdict=None,
        social_media={
            "generated": False,
            "reason": "Paper not recommended for promotion",
        },
    )


@pytest.fixture
def mock_dspy_prediction():
    """Mock DSPy prediction object for testing."""
    prediction = Mock(spec=dspy.Prediction)
    prediction.title = "Test Paper Title"
    prediction.authors = ["Test Author"]
    prediction.abstract = "Test abstract content"
    prediction.keywords = ["test", "paper", "keywords"]
    return prediction


@pytest.fixture
def sample_arxiv_response():
    """Sample arXiv API XML response for testing."""
    return """<?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
        <entry>
            <id>http://arxiv.org/abs/1706.03762v5</id>
            <title>Attention Is All You Need</title>
            <summary>The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...</summary>
            <published>2017-06-12T17:57:34Z</published>
            <updated>2017-12-06T15:49:32Z</updated>
            <author><name>Ashish Vaswani</name></author>
            <author><name>Noam Shazeer</name></author>
            <category term="cs.CL" />
            <category term="cs.LG" />
        </entry>
    </feed>"""


@pytest.fixture
def sample_semantic_scholar_response():
    """Sample Semantic Scholar API JSON response for testing."""
    return {
        "data": [
            {
                "title": "Attention Is All You Need",
                "authors": [{"name": "Ashish Vaswani"}, {"name": "Noam Shazeer"}],
                "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...",
                "year": 2017,
                "venue": "NIPS",
                "citationCount": 50000,
                "paperId": "204e3073870fae3d05bcbc2f6a8e263d9b72e776",
                "url": "https://www.semanticscholar.org/paper/204e3073870fae3d05bcbc2f6a8e263d9b72e776",
                "externalIds": {"ArXiv": "1706.03762"},
                "fieldsOfStudy": ["Computer Science"],
            }
        ]
    }
