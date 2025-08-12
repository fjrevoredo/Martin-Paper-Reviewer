"""
Sample paper data for testing.

Contains realistic paper content and metadata for use in tests.
"""

from typing import Any, Dict, List

# Sample paper based on the famous "Attention Is All You Need" paper
TRANSFORMER_PAPER = {
    "title": "Attention Is All You Need",
    "authors": [
        "Ashish Vaswani",
        "Noam Shazeer",
        "Niki Parmar",
        "Jakob Uszkoreit",
        "Llion Jones",
        "Aidan N. Gomez",
        "Lukasz Kaiser",
        "Illia Polosukhin",
    ],
    "abstract": """The dominant sequence transduction models are based on complex recurrent or 
    convolutional neural networks that include an encoder and a decoder. The best performing 
    models also connect the encoder and decoder through an attention mechanism. We propose a 
    new simple network architecture, the Transformer, based solely on attention mechanisms, 
    dispensing with recurrence and convolutions entirely.""",
    "keywords": [
        "attention",
        "transformer",
        "neural networks",
        "machine translation",
        "sequence modeling",
        "self-attention",
    ],
    "year": 2017,
    "venue": "NIPS",
    "pdf_url": "https://arxiv.org/pdf/1706.03762.pdf",
    "full_text": """
    Attention Is All You Need
    
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
    machine translation. Numerous efforts have since continued to push the boundaries 
    of recurrent language models and encoder-decoder architectures.
    
    2 Background
    The goal of reducing sequential computation also forms the foundation of the 
    Extended Neural GPU, ByteNet and ConvS2S, all of which use convolutional neural 
    networks as basic building block, computing hidden representations in parallel 
    for all input and output positions.
    
    3 Model Architecture
    Most competitive neural sequence transduction models have an encoder-decoder 
    structure. Here, the encoder maps an input sequence of symbol representations 
    to a sequence of continuous representations. Given z, the decoder then generates 
    an output sequence of symbols one element at a time.
    
    4 Why Self-Attention
    In this section we compare various aspects of self-attention layers to the 
    recurrent and convolutional layers commonly used for mapping one variable-length 
    sequence of symbol representations to another sequence of equal length.
    
    5 Training
    This section describes the training regime for our models. We trained on the 
    standard WMT 2014 English-German dataset consisting of about 4.5 million 
    sentence pairs.
    
    6 Results
    On the WMT 2014 English-to-German translation task, the big transformer model 
    (Transformer (big) in the table) achieves 28.4 BLEU, improving over the 
    previously reported best results, including ensembles, by over 2 BLEU.
    
    7 Conclusion
    In this work, we presented the Transformer, the first sequence transduction 
    model based entirely on attention, replacing the recurrent layers most commonly 
    used in encoder-decoder architectures with multi-headed self-attention.
    
    References
    [1] Dzmitry Bahdanau, Kyunghyun Cho, and Yoshua Bengio. Neural machine translation 
    by jointly learning to align and translate. arXiv preprint arXiv:1409.0473, 2014.
    [2] Kyunghyun Cho, Bart van Merrienboer, Caglar Gulcehre, Dzmitry Bahdanau, 
    Fethi Bougares, Holger Schwenk, and Yoshua Bengio. Learning phrase representations 
    using rnn encoder-decoder for statistical machine translation. arXiv preprint 
    arXiv:1406.1078, 2014.
    """,
    "sections": {
        "abstract": """The dominant sequence transduction models are based on complex recurrent or 
        convolutional neural networks that include an encoder and a decoder. The best 
        performing models also connect the encoder and decoder through an attention 
        mechanism. We propose a new simple network architecture, the Transformer, 
        based solely on attention mechanisms, dispensing with recurrence and convolutions 
        entirely.""",
        "introduction": """Recurrent neural networks, long short-term memory and gated recurrent neural 
        networks in particular, have been firmly established as state of the art approaches 
        in sequence modeling and transduction problems such as language modeling and 
        machine translation. Numerous efforts have since continued to push the boundaries 
        of recurrent language models and encoder-decoder architectures.""",
        "methodology": """Most competitive neural sequence transduction models have an encoder-decoder 
        structure. Here, the encoder maps an input sequence of symbol representations 
        to a sequence of continuous representations. Given z, the decoder then generates 
        an output sequence of symbols one element at a time.""",
        "results": """On the WMT 2014 English-to-German translation task, the big transformer model 
        (Transformer (big) in the table) achieves 28.4 BLEU, improving over the 
        previously reported best results, including ensembles, by over 2 BLEU.""",
        "conclusion": """In this work, we presented the Transformer, the first sequence transduction 
        model based entirely on attention, replacing the recurrent layers most commonly 
        used in encoder-decoder architectures with multi-headed self-attention.""",
        "references": """[1] Dzmitry Bahdanau, Kyunghyun Cho, and Yoshua Bengio. Neural machine translation 
        by jointly learning to align and translate. arXiv preprint arXiv:1409.0473, 2014.
        [2] Kyunghyun Cho, Bart van Merrienboer, Caglar Gulcehre, Dzmitry Bahdanau, 
        Fethi Bougares, Holger Schwenk, and Yoshua Bengio. Learning phrase representations 
        using rnn encoder-decoder for statistical machine translation. arXiv preprint 
        arXiv:1406.1078, 2014.""",
    },
}


# Sample paper with minimal content for edge case testing
MINIMAL_PAPER = {
    "title": "A Short Paper",
    "authors": ["John Doe"],
    "abstract": "This is a minimal abstract.",
    "keywords": ["test"],
    "year": 2023,
    "venue": "Test Conference",
    "pdf_url": "https://example.com/minimal.pdf",
    "full_text": "A Short Paper\n\nAbstract\nThis is a minimal abstract.\n\nConclusion\nThis is a short conclusion.",
    "sections": {
        "abstract": "This is a minimal abstract.",
        "introduction": "",
        "methodology": "",
        "results": "",
        "conclusion": "This is a short conclusion.",
        "references": "",
    },
}


# Sample paper with missing sections for testing edge cases
INCOMPLETE_PAPER = {
    "title": "Incomplete Paper Example",
    "authors": ["Jane Smith", "Bob Johnson"],
    "abstract": "",
    "keywords": [],
    "year": 2022,
    "venue": "",
    "pdf_url": "https://example.com/incomplete.pdf",
    "full_text": "Incomplete Paper Example\n\nSome content without clear sections.",
    "sections": {
        "abstract": "",
        "introduction": "",
        "methodology": "",
        "results": "",
        "conclusion": "",
        "references": "",
    },
}


# Sample papers list for parameterized testing
SAMPLE_PAPERS = [TRANSFORMER_PAPER, MINIMAL_PAPER, INCOMPLETE_PAPER]


def get_sample_paper(paper_type: str = "transformer") -> Dict[str, Any]:
    """
    Get a sample paper by type.

    Args:
        paper_type: Type of paper ("transformer", "minimal", "incomplete")

    Returns:
        Dictionary containing paper data
    """
    paper_map = {
        "transformer": TRANSFORMER_PAPER,
        "minimal": MINIMAL_PAPER,
        "incomplete": INCOMPLETE_PAPER,
    }

    return paper_map.get(paper_type, TRANSFORMER_PAPER)


def get_sample_paper_text(paper_type: str = "transformer") -> str:
    """
    Get sample paper full text by type.

    Args:
        paper_type: Type of paper ("transformer", "minimal", "incomplete")

    Returns:
        Full text content of the paper
    """
    paper = get_sample_paper(paper_type)
    return paper["full_text"]


def get_sample_sections(paper_type: str = "transformer") -> Dict[str, str]:
    """
    Get sample paper sections by type.

    Args:
        paper_type: Type of paper ("transformer", "minimal", "incomplete")

    Returns:
        Dictionary mapping section names to content
    """
    paper = get_sample_paper(paper_type)
    return paper["sections"]
