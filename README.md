# Martin - AI-Powered Research Paper Reviewer

![Martin Logo](branding/martin-small.png)

[![CI](https://github.com/fjrevoredo/Martin-Paper-Reviewer/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/fjrevoredo/Martin-Paper-Reviewer/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Martin automatically analyzes research papers and generates comprehensive reviews with reproducibility scores, impact assessments, and structured recommendations.

## Features

- **PDF Analysis**: Extracts and analyzes paper content, methodology, and contributions
- **Reproducibility Scoring**: Quantitative assessment (1-10 scale) with detailed justification  
- **Literature Search**: Compares against related papers using arXiv and Semantic Scholar
- **Impact Evaluation**: Predicts academic and societal impact potential
- **Professional Reports**: Generates structured Markdown reviews with clear recommendations

## Installation

```bash
git clone https://github.com/fjrevoredo/Martin-Paper-Reviewer.git
cd Martin-Paper-Reviewer

# Quick setup
./setup.sh  # Linux/macOS
setup.bat   # Windows

# Configure API key
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY from https://openrouter.ai/keys
```

## Usage

```bash
# Analyze a paper
martin https://arxiv.org/pdf/1706.03762.pdf

# Save to file
martin https://arxiv.org/pdf/1706.03762.pdf -o review.md

# Common options
martin paper.pdf --verbose --no-social --max-results 3
```

**Key Options:**
- `-o, --output`: Save to file
- `--verbose`: Show detailed progress  
- `--no-social`: Skip social media content
- `--max-results N`: Compare against N papers per database

## Configuration

**Required:**
- OpenRouter API key in `.env` file ([get one here](https://openrouter.ai/keys))

**Optional (for enhanced literature search):**
```bash
# Add to .env file
SEMANTIC_SCHOLAR_API_KEY=your_key_here
```

**Supported AI Models:**
- `openai/gpt-4` (recommended)
- `openai/gpt-4o-mini` (good balance)  
- `openai/gpt-3.5-turbo` (fast/cheap)

## Output

Martin generates structured reviews with:
- Executive summary with scores and recommendations
- Methodology analysis with reproducibility scoring (1-10)
- Contribution assessment and literature comparison
- Impact evaluation and final verdict
- Social media content (for highly-rated papers)

## Requirements

- Python 3.8+
- OpenRouter API key
- Internet connection

## License

MIT License - see [LICENSE](LICENSE) file.

## Support

- [Issues](https://github.com/fjrevoredo/Martin-Paper-Reviewer/issues) - Bug reports and feature requests
- [Contributing Guide](CONTRIBUTING.md) - Development setup and guidelines