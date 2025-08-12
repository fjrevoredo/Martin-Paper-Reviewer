# Contributing to Martin

Thank you for your interest in contributing to Martin! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment
4. Create a branch for your changes
5. Make your changes
6. Test your changes
7. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- OpenRouter API key (for testing)

### Installation

1. Clone your fork:
```bash
git clone https://github.com/YOUR_USERNAME/martin.git
cd martin
```

2. Set up virtual environment:
```bash
# Using uv (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# Or using venv
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

4. Verify installation:
```bash
python -m pytest
python -m martin --help
```

## Making Changes

### Branch Naming

Use descriptive branch names:
- `feature/add-new-api-integration`
- `fix/handle-pdf-parsing-error`
- `docs/update-installation-guide`
- `test/add-integration-tests`

### Commit Messages

Follow conventional commit format:
- `feat: add support for new academic database`
- `fix: resolve PDF parsing issue with special characters`
- `docs: update README with new configuration options`
- `test: add unit tests for literature comparison`
- `refactor: simplify error handling logic`

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=martin

# Run specific test file
python -m pytest tests/test_real_literature_comparison.py

# Run tests with verbose output
python -m pytest -v
```

### Writing Tests

- Add tests for all new functionality
- Maintain test coverage above 90%
- Use descriptive test names
- Mock external API calls in unit tests
- Include both positive and negative test cases

### Test Structure

```python
def test_feature_description():
    """Test that feature works correctly under normal conditions."""
    # Arrange
    setup_test_data()
    
    # Act
    result = function_under_test()
    
    # Assert
    assert result.expected_property == expected_value
```

## Code Style

### Python Style Guide

We follow PEP 8 with some modifications:

- Line length: 88 characters (Black default)
- Use type hints for all function parameters and return values
- Use descriptive variable and function names
- Add docstrings to all public functions and classes

### Formatting Tools

Before submitting, run these tools:

```bash
# Format code
black .
isort .

# Check style
flake8 .

# Type checking (optional but recommended)
mypy martin/
```

### Docstring Format

Use Google-style docstrings:

```python
def search_papers(query: str, max_results: int = 10) -> List[Paper]:
    """
    Search for academic papers matching the query.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        
    Returns:
        List of Paper objects matching the query
        
    Raises:
        ValueError: If query is empty or invalid
        APIError: If external API request fails
    """
```

## Submitting Changes

### Pull Request Process

1. **Update Documentation**: Ensure README, docstrings, and other docs are updated
2. **Add Tests**: Include tests for new functionality
3. **Run Tests**: Ensure all tests pass locally
4. **Format Code**: Run black, isort, and flake8
5. **Update Changelog**: Add entry to CHANGELOG.md if applicable
6. **Create PR**: Use the pull request template

### Pull Request Template

When creating a PR, include:

- **Description**: What changes were made and why
- **Type of Change**: Bug fix, new feature, documentation, etc.
- **Testing**: How the changes were tested
- **Checklist**: Confirm all requirements are met

### Review Process

- All PRs require at least one review
- Address reviewer feedback promptly
- Keep PRs focused and reasonably sized
- Be responsive to questions and suggestions

## Reporting Issues

### Bug Reports

When reporting bugs, include:

- **Environment**: Python version, OS, package versions
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Error Messages**: Full error messages and stack traces
- **Additional Context**: Any other relevant information

### Feature Requests

When requesting features, include:

- **Problem Description**: What problem does this solve?
- **Proposed Solution**: How should this work?
- **Alternatives**: Other solutions you've considered
- **Use Cases**: Specific examples of how this would be used

### Questions and Help

For questions:

- Check existing documentation first
- Search existing issues
- Use GitHub Discussions for general questions
- Create an issue for specific problems

## Development Guidelines

### Adding New Features

1. **Discuss First**: For major features, create an issue to discuss the approach
2. **Start Small**: Break large features into smaller, reviewable chunks
3. **Maintain Compatibility**: Avoid breaking changes when possible
4. **Document Everything**: Update docs, add examples, write tests
5. **Consider Performance**: Profile and optimize performance-critical code

### API Design Principles

- **Consistency**: Follow existing patterns and conventions
- **Simplicity**: Keep APIs simple and intuitive
- **Flexibility**: Allow customization without complexity
- **Error Handling**: Provide clear, actionable error messages
- **Documentation**: Include comprehensive docstrings and examples

### External Dependencies

- **Minimize Dependencies**: Only add dependencies that provide significant value
- **Version Pinning**: Pin major versions, allow minor updates
- **License Compatibility**: Ensure all dependencies have compatible licenses
- **Security**: Regularly update dependencies for security patches

## Getting Help

- **Documentation**: Check README.md and other docs
- **Issues**: Search existing issues for similar problems
- **Discussions**: Use GitHub Discussions for questions
- **Contact**: Reach out to maintainers for urgent issues

## Recognition

Contributors will be recognized in:
- CHANGELOG.md for significant contributions
- GitHub contributors list
- Special thanks in release notes

Thank you for contributing to Martin!