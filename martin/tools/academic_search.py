"""
Academic Search Engine Tool

Simulates academic paper search functionality similar to Semantic Scholar,
ArXiv, or Google Scholar. Provides realistic mock results for literature
comparison and contextualization.
"""

import random
import re
import time
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class SearchResult:
    """Represents a single academic paper search result."""

    title: str
    authors: List[str]
    abstract: str
    year: int
    venue: str
    citation_count: int
    url: str
    relevance_score: float  # 0.0 to 1.0


class AcademicSearchEngine:
    """
    Simulates academic paper search functionality.

    Provides realistic mock search results based on query terms,
    simulating the behavior of academic search engines like
    Semantic Scholar or ArXiv.
    """

    def __init__(self, max_results: int = 10, simulate_delay: bool = True):
        """
        Initialize the academic search engine.

        Args:
            max_results: Maximum number of results to return per search
            simulate_delay: Whether to simulate network delay
        """
        self.max_results = max_results
        self.simulate_delay = simulate_delay

        # Mock database of academic papers for realistic results
        self._mock_papers = self._initialize_mock_database()

    def search(
        self, query: str, max_results: Optional[int] = None
    ) -> List[SearchResult]:
        """
        Search for academic papers based on query.

        Args:
            query: Search query string
            max_results: Maximum results to return (overrides default)

        Returns:
            List of SearchResult objects ranked by relevance

        Raises:
            ValueError: If query is empty or invalid
            RuntimeError: If search fails (simulated network issues)
        """
        if not query or not query.strip():
            raise ValueError("Search query cannot be empty")

        # Simulate network delay
        if self.simulate_delay:
            time.sleep(random.uniform(0.1, 0.5))

        # Simulate occasional search failures (1% chance, lower for testing)
        if random.random() < 0.01:
            raise RuntimeError("Search service temporarily unavailable")

        # Process query and find relevant papers
        results = self._process_search_query(query)

        # Limit results
        limit = max_results or self.max_results
        return results[:limit]

    def search_multiple_queries(
        self, queries: List[str]
    ) -> Dict[str, List[SearchResult]]:
        """
        Search multiple queries and return combined results.

        Args:
            queries: List of search query strings

        Returns:
            Dictionary mapping queries to their search results
        """
        results = {}

        for query in queries:
            try:
                results[query] = self.search(query)
            except Exception as e:
                # Log error but continue with other queries
                print(f"Warning: Search failed for query '{query}': {e}")
                results[query] = []

        return results

    def _process_search_query(self, query: str) -> List[SearchResult]:
        """
        Process search query and return relevant mock results.

        Args:
            query: Search query string

        Returns:
            List of relevant SearchResult objects
        """
        query_lower = query.lower()
        query_terms = self._extract_query_terms(query_lower)

        # Find relevant papers from mock database
        relevant_papers = []

        for paper in self._mock_papers:
            relevance = self._calculate_relevance(paper, query_terms)
            if relevance > 0.1:  # Minimum relevance threshold
                paper_copy = paper.copy()
                paper_copy["relevance_score"] = relevance
                relevant_papers.append(paper_copy)

        # Sort by relevance score
        relevant_papers.sort(key=lambda x: x["relevance_score"], reverse=True)

        # Convert to SearchResult objects
        results = []
        for paper in relevant_papers:
            result = SearchResult(
                title=paper["title"],
                authors=paper["authors"],
                abstract=paper["abstract"],
                year=paper["year"],
                venue=paper["venue"],
                citation_count=paper["citation_count"],
                url=paper["url"],
                relevance_score=paper["relevance_score"],
            )
            results.append(result)

        return results

    def _extract_query_terms(self, query: str) -> List[str]:
        """Extract meaningful terms from search query."""
        # Remove common stop words
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "can",
            "this",
            "that",
            "these",
            "those",
        }

        # Extract words and filter
        words = re.findall(r"\b\w+\b", query.lower())
        terms = [word for word in words if word not in stop_words and len(word) > 2]

        return terms

    def _calculate_relevance(self, paper: Dict, query_terms: List[str]) -> float:
        """
        Calculate relevance score between paper and query terms.

        Args:
            paper: Paper dictionary from mock database
            query_terms: List of query terms

        Returns:
            Relevance score between 0.0 and 1.0
        """
        if not query_terms:
            return 0.0

        # Combine searchable text
        searchable_text = (
            paper["title"] + " " + paper["abstract"] + " " + " ".join(paper["keywords"])
        ).lower()

        # Calculate term matches
        matches = 0
        total_weight = 0

        for term in query_terms:
            # Title matches are weighted more heavily
            title_matches = paper["title"].lower().count(term)
            abstract_matches = paper["abstract"].lower().count(term)
            keyword_matches = sum(kw.lower().count(term) for kw in paper["keywords"])

            # Weighted scoring
            term_score = (
                title_matches * 3.0 + abstract_matches * 1.0 + keyword_matches * 2.0
            )

            matches += term_score
            total_weight += 3.0  # Maximum possible weight per term

        # Normalize score
        if total_weight == 0:
            return 0.0

        base_score = min(matches / total_weight, 1.0)

        # Add some randomness to simulate real search ranking
        noise = random.uniform(-0.1, 0.1)
        final_score = max(0.0, min(1.0, base_score + noise))

        return final_score

    def _initialize_mock_database(self) -> List[Dict]:
        """Initialize mock database of academic papers."""

        # This would normally come from a real academic database
        # For simulation, we create a diverse set of realistic papers
        mock_papers = [
            {
                "title": "Attention Is All You Need",
                "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
                "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms.",
                "year": 2017,
                "venue": "NeurIPS",
                "citation_count": 45000,
                "url": "https://arxiv.org/abs/1706.03762",
                "keywords": [
                    "attention",
                    "transformer",
                    "neural networks",
                    "sequence modeling",
                ],
            },
            {
                "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
                "authors": ["Jacob Devlin", "Ming-Wei Chang", "Kenton Lee"],
                "abstract": "We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers. Unlike recent language representation models, BERT is designed to pre-train deep bidirectional representations from unlabeled text.",
                "year": 2018,
                "venue": "NAACL",
                "citation_count": 35000,
                "url": "https://arxiv.org/abs/1810.04805",
                "keywords": ["bert", "transformers", "language models", "pre-training"],
            },
            {
                "title": "Deep Residual Learning for Image Recognition",
                "authors": ["Kaiming He", "Xiangyu Zhang", "Shaoqing Ren"],
                "abstract": "Deeper neural networks are more difficult to train. We present a residual learning framework to ease the training of networks that are substantially deeper than those used previously.",
                "year": 2016,
                "venue": "CVPR",
                "citation_count": 50000,
                "url": "https://arxiv.org/abs/1512.03385",
                "keywords": [
                    "residual networks",
                    "deep learning",
                    "computer vision",
                    "image recognition",
                ],
            },
            {
                "title": "Generative Adversarial Networks",
                "authors": ["Ian Goodfellow", "Jean Pouget-Abadie", "Mehdi Mirza"],
                "abstract": "We propose a new framework for estimating generative models via an adversarial process, in which we simultaneously train two models: a generative model G that captures the data distribution, and a discriminative model D.",
                "year": 2014,
                "venue": "NeurIPS",
                "citation_count": 40000,
                "url": "https://arxiv.org/abs/1406.2661",
                "keywords": [
                    "generative models",
                    "adversarial training",
                    "neural networks",
                    "machine learning",
                ],
            },
            {
                "title": "Adam: A Method for Stochastic Optimization",
                "authors": ["Diederik P. Kingma", "Jimmy Ba"],
                "abstract": "We introduce Adam, an algorithm for first-order gradient-based optimization of stochastic objective functions, based on adaptive estimates of lower-order moments.",
                "year": 2014,
                "venue": "ICLR",
                "citation_count": 30000,
                "url": "https://arxiv.org/abs/1412.6980",
                "keywords": [
                    "optimization",
                    "gradient descent",
                    "machine learning",
                    "algorithms",
                ],
            },
            {
                "title": "Language Models are Few-Shot Learners",
                "authors": ["Tom B. Brown", "Benjamin Mann", "Nick Ryder"],
                "abstract": "Recent work has demonstrated substantial gains on many NLP tasks and benchmarks by pre-training on a large corpus of text followed by fine-tuning on a specific task. We show that scaling up language models greatly improves task-agnostic, few-shot performance.",
                "year": 2020,
                "venue": "NeurIPS",
                "citation_count": 25000,
                "url": "https://arxiv.org/abs/2005.14165",
                "keywords": [
                    "language models",
                    "few-shot learning",
                    "gpt-3",
                    "natural language processing",
                ],
            },
            {
                "title": "Convolutional Neural Networks for Sentence Classification",
                "authors": ["Yoon Kim"],
                "abstract": "We report on a series of experiments with convolutional neural networks (CNN) trained on top of pre-trained word vectors for sentence-level classification tasks.",
                "year": 2014,
                "venue": "EMNLP",
                "citation_count": 8000,
                "url": "https://arxiv.org/abs/1408.5882",
                "keywords": [
                    "convolutional neural networks",
                    "text classification",
                    "word embeddings",
                    "nlp",
                ],
            },
            {
                "title": "Neural Machine Translation by Jointly Learning to Align and Translate",
                "authors": ["Dzmitry Bahdanau", "Kyunghyun Cho", "Yoshua Bengio"],
                "abstract": "Neural machine translation is a recently proposed approach to machine translation. Unlike the traditional statistical machine translation, the neural machine translation aims at building a single neural network.",
                "year": 2014,
                "venue": "ICLR",
                "citation_count": 15000,
                "url": "https://arxiv.org/abs/1409.0473",
                "keywords": [
                    "machine translation",
                    "attention mechanism",
                    "neural networks",
                    "sequence to sequence",
                ],
            },
            {
                "title": "Dropout: A Simple Way to Prevent Neural Networks from Overfitting",
                "authors": ["Nitish Srivastava", "Geoffrey Hinton", "Alex Krizhevsky"],
                "abstract": "Deep neural nets with a large number of parameters are very powerful machine learning systems. However, overfitting is a serious problem in such networks.",
                "year": 2014,
                "venue": "JMLR",
                "citation_count": 20000,
                "url": "http://jmlr.org/papers/v15/srivastava14a.html",
                "keywords": [
                    "dropout",
                    "regularization",
                    "neural networks",
                    "overfitting",
                ],
            },
            {
                "title": "Batch Normalization: Accelerating Deep Network Training",
                "authors": ["Sergey Ioffe", "Christian Szegedy"],
                "abstract": "Training Deep Neural Networks is complicated by the fact that the distribution of each layers inputs changes during training, as the parameters of the previous layers change.",
                "year": 2015,
                "venue": "ICML",
                "citation_count": 18000,
                "url": "https://arxiv.org/abs/1502.03167",
                "keywords": [
                    "batch normalization",
                    "deep learning",
                    "training acceleration",
                    "neural networks",
                ],
            },
        ]

        return mock_papers
