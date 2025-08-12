"""
Sample API responses for testing external service integrations.

Contains realistic mock responses from arXiv, Semantic Scholar, and other APIs.
"""

from typing import Any, Dict, List

# Sample arXiv API XML responses
ARXIV_SUCCESSFUL_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>ArXiv Query: search_query=attention+mechanism</title>
    <id>http://arxiv.org/api/query?search_query=attention+mechanism</id>
    <updated>2023-12-01T00:00:00-05:00</updated>
    <totalResults>2</totalResults>
    <startIndex>0</startIndex>
    <itemsPerPage>10</itemsPerPage>
    <entry>
        <id>http://arxiv.org/abs/1706.03762v5</id>
        <title>Attention Is All You Need</title>
        <summary>The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.</summary>
        <published>2017-06-12T17:57:34Z</published>
        <updated>2017-12-06T15:49:32Z</updated>
        <author><name>Ashish Vaswani</name></author>
        <author><name>Noam Shazeer</name></author>
        <author><name>Niki Parmar</name></author>
        <category term="cs.CL" scheme="http://arxiv.org/schemas/atom"/>
        <category term="cs.LG" scheme="http://arxiv.org/schemas/atom"/>
        <link href="http://arxiv.org/abs/1706.03762v5" rel="alternate" type="text/html"/>
        <link title="pdf" href="http://arxiv.org/pdf/1706.03762v5.pdf" rel="related" type="application/pdf"/>
    </entry>
    <entry>
        <id>http://arxiv.org/abs/1409.0473v7</id>
        <title>Neural Machine Translation by Jointly Learning to Align and Translate</title>
        <summary>Neural machine translation is a recently proposed approach to machine translation. Unlike the traditional statistical machine translation, the neural machine translation aims at building a single neural network that can be jointly tuned to maximize the translation performance.</summary>
        <published>2014-09-01T20:00:09Z</published>
        <updated>2016-05-19T20:02:44Z</updated>
        <author><name>Dzmitry Bahdanau</name></author>
        <author><name>Kyunghyun Cho</name></author>
        <author><name>Yoshua Bengio</name></author>
        <category term="cs.CL" scheme="http://arxiv.org/schemas/atom"/>
        <category term="cs.LG" scheme="http://arxiv.org/schemas/atom"/>
        <category term="cs.NE" scheme="http://arxiv.org/schemas/atom"/>
        <category term="stat.ML" scheme="http://arxiv.org/schemas/atom"/>
        <link href="http://arxiv.org/abs/1409.0473v7" rel="alternate" type="text/html"/>
        <link title="pdf" href="http://arxiv.org/pdf/1409.0473v7.pdf" rel="related" type="application/pdf"/>
    </entry>
</feed>"""

ARXIV_EMPTY_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>ArXiv Query: search_query=nonexistent+query</title>
    <id>http://arxiv.org/api/query?search_query=nonexistent+query</id>
    <updated>2023-12-01T00:00:00-05:00</updated>
    <totalResults>0</totalResults>
    <startIndex>0</startIndex>
    <itemsPerPage>10</itemsPerPage>
</feed>"""

ARXIV_MALFORMED_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<invalid-xml>
    <missing-closing-tag>
</invalid-xml>"""


# Sample Semantic Scholar API JSON responses
SEMANTIC_SCHOLAR_SUCCESSFUL_RESPONSE = {
    "data": [
        {
            "paperId": "204e3073870fae3d05bcbc2f6a8e263d9b72e776",
            "title": "Attention Is All You Need",
            "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.",
            "venue": "NIPS",
            "year": 2017,
            "authors": [
                {"authorId": "1699545", "name": "Ashish Vaswani"},
                {"authorId": "2055477", "name": "Noam Shazeer"},
                {"authorId": "2056142", "name": "Niki Parmar"},
                {"authorId": "1728024", "name": "Jakob Uszkoreit"},
            ],
            "citationCount": 50000,
            "referenceCount": 23,
            "influentialCitationCount": 8500,
            "isOpenAccess": True,
            "fieldsOfStudy": ["Computer Science"],
            "publicationTypes": ["JournalArticle"],
            "publicationDate": "2017-06-12",
            "journal": {
                "name": "Neural Information Processing Systems",
                "volume": "30",
            },
            "externalIds": {
                "ArXiv": "1706.03762",
                "DBLP": "conf/nips/VaswaniSPUJGKP17",
                "MAG": "2963403868",
            },
            "url": "https://www.semanticscholar.org/paper/204e3073870fae3d05bcbc2f6a8e263d9b72e776",
        },
        {
            "paperId": "0737b270767fc6963395df9dccdcb2faa36e5b85",
            "title": "Neural Machine Translation by Jointly Learning to Align and Translate",
            "abstract": "Neural machine translation is a recently proposed approach to machine translation. Unlike the traditional statistical machine translation, the neural machine translation aims at building a single neural network that can be jointly tuned to maximize the translation performance.",
            "venue": "ICLR",
            "year": 2015,
            "authors": [
                {"authorId": "1741101", "name": "Dzmitry Bahdanau"},
                {"authorId": "1692192", "name": "Kyunghyun Cho"},
                {"authorId": "1695689", "name": "Yoshua Bengio"},
            ],
            "citationCount": 25000,
            "referenceCount": 45,
            "influentialCitationCount": 4200,
            "isOpenAccess": True,
            "fieldsOfStudy": ["Computer Science"],
            "publicationTypes": ["JournalArticle"],
            "publicationDate": "2014-09-01",
            "journal": {"name": "International Conference on Learning Representations"},
            "externalIds": {"ArXiv": "1409.0473", "DBLP": "journals/corr/BahdanauCB14"},
            "url": "https://www.semanticscholar.org/paper/0737b270767fc6963395df9dccdcb2faa36e5b85",
        },
    ],
    "total": 2,
    "offset": 0,
    "next": None,
}

SEMANTIC_SCHOLAR_EMPTY_RESPONSE = {"data": [], "total": 0, "offset": 0, "next": None}

SEMANTIC_SCHOLAR_MALFORMED_RESPONSE = {
    "error": "Invalid query parameters",
    "message": "The query parameter is required",
}


# Sample HTTP error responses
HTTP_404_RESPONSE = {
    "status_code": 404,
    "reason": "Not Found",
    "text": "The requested resource was not found",
}

HTTP_429_RESPONSE = {
    "status_code": 429,
    "reason": "Too Many Requests",
    "headers": {"Retry-After": "60"},
    "text": "Rate limit exceeded",
}

HTTP_500_RESPONSE = {
    "status_code": 500,
    "reason": "Internal Server Error",
    "text": "Internal server error occurred",
}


# Sample PDF content for testing PDF extraction
SAMPLE_PDF_CONTENT = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Sample PDF Content) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
299
%%EOF"""


def get_arxiv_response(response_type: str = "successful") -> str:
    """
    Get sample arXiv API response by type.

    Args:
        response_type: Type of response ("successful", "empty", "malformed")

    Returns:
        XML response string
    """
    response_map = {
        "successful": ARXIV_SUCCESSFUL_RESPONSE,
        "empty": ARXIV_EMPTY_RESPONSE,
        "malformed": ARXIV_MALFORMED_RESPONSE,
    }

    return response_map.get(response_type, ARXIV_SUCCESSFUL_RESPONSE)


def get_semantic_scholar_response(response_type: str = "successful") -> Dict[str, Any]:
    """
    Get sample Semantic Scholar API response by type.

    Args:
        response_type: Type of response ("successful", "empty", "malformed")

    Returns:
        JSON response dictionary
    """
    response_map = {
        "successful": SEMANTIC_SCHOLAR_SUCCESSFUL_RESPONSE,
        "empty": SEMANTIC_SCHOLAR_EMPTY_RESPONSE,
        "malformed": SEMANTIC_SCHOLAR_MALFORMED_RESPONSE,
    }

    return response_map.get(response_type, SEMANTIC_SCHOLAR_SUCCESSFUL_RESPONSE)


def get_http_error_response(status_code: int = 404) -> Dict[str, Any]:
    """
    Get sample HTTP error response by status code.

    Args:
        status_code: HTTP status code (404, 429, 500)

    Returns:
        Error response dictionary
    """
    response_map = {
        404: HTTP_404_RESPONSE,
        429: HTTP_429_RESPONSE,
        500: HTTP_500_RESPONSE,
    }

    return response_map.get(status_code, HTTP_404_RESPONSE)
