# Martin Test Suite

This directory contains comprehensive unit tests for Martin.

## Test Structure

```
tests/
├── conftest.py                    # Shared fixtures and configuration
├── fixtures/                     # Test data
│   ├── sample_papers.py          # Sample paper content
│   └── api_responses.py          # Sample API responses
├── test_config.py                # Configuration tests
├── test_main.py                  # CLI tests
├── test_paper_reviewer.py        # Main orchestration tests
├── test_formatter.py             # Output formatting tests
├── test_paper_text.py            # PaperText model tests
├── test_pdf_extractor.py         # PDF extraction tests
├── test_arxiv_client.py          # arXiv client tests (existing)
├── test_semantic_scholar_client.py # Semantic Scholar tests (existing)
└── test_real_academic_search.py  # Academic search tests (existing)
```

## Running Tests

### Run all tests
```bash
python -m pytest tests/
```

### Run with coverage
```bash
python -m pytest tests/ --cov=martin --cov-report=term-missing
```

### Run specific test files
```bash
python -m pytest tests/test_paper_text.py -v
python -m pytest tests/test_config.py -v
```

## Test Coverage

The test suite aims for 85%+ code coverage across all modules. Current coverage focuses on:

- **Data Models**: 100% coverage of PaperText model validation and utility methods
- **Configuration**: 100% coverage of Config class and DSPy setup
- **Core Business Logic**: High coverage of text processing, formatting, and validation
- **Error Handling**: Comprehensive testing of edge cases and failure scenarios

## Test Categories

### Unit Tests (Primary Focus)
- Individual functions and classes with minimal mocking
- Fast execution (< 30 seconds for full suite)
- Focus on business logic, data transformations, error handling

### Key Testing Priorities
1. **Critical Path Functions**: Core logic that affects review quality
2. **Error Handling**: Edge cases and failure scenarios
3. **Data Processing**: Text parsing, formatting, validation
4. **Configuration**: Setup and validation logic

## Mocking Strategy

**Principle**: Mock only external I/O and dependencies that cannot be controlled in tests.

### What We Mock:
- HTTP requests (requests.Session.get/post)
- File system operations (when testing error conditions)
- DSPy language model calls (dspy.configure, actual LLM calls)
- Time-dependent operations (time.sleep)

### What We DON'T Mock:
- Internal application logic and data transformations
- Pydantic model operations
- String processing and formatting
- Data structure manipulations
- Pure functions without side effects

## Test Fixtures

### Shared Fixtures (conftest.py)
- `sample_paper_text`: Complete paper text content
- `sample_extraction_result`: Mock extraction results
- `sample_methodology_result`: Mock methodology analysis
- `sample_complete_result`: Complete review result for integration testing

### Sample Data (fixtures/)
- `sample_papers.py`: Realistic paper content based on actual research papers
- `api_responses.py`: Mock API responses for external services

## Current Status

### Working Tests
- ✅ `test_paper_text.py`: 23/23 tests passing - PaperText model validation
- ✅ `test_config.py`: 24/24 tests passing - Configuration and DSPy setup

### In Progress
- 🔧 `test_paper_reviewer.py`: Main orchestration tests (needs results dict fixes)
- 🔧 `test_formatter.py`: Output formatting tests (minor assertion fixes needed)
- 🔧 `test_main.py`: CLI tests (mock setup adjustments needed)
- 🔧 `test_pdf_extractor.py`: PDF extraction tests (section parsing edge cases)

### Existing Tests
- ✅ `test_real_literature_comparison.py`: Comprehensive literature search tests
- ✅ Academic search integration tests (arXiv, Semantic Scholar)

## Known Issues & Fixes Needed

1. **Results Dictionary Initialization**: Many tests expect `results` dict to have `errors` and `warnings` keys
2. **Mock Setup**: Some mocks need better configuration for realistic behavior
3. **Section Parsing**: PDF section parsing tests need refinement for edge cases
4. **Assertion Adjustments**: Some test assertions need updates to match actual behavior

## Performance

- Target execution time: < 30 seconds for full suite
- Current execution time for working tests: < 1 second
- Memory usage: Minimal due to focused mocking strategy

## Maintenance

Tests are designed to be:
- **Easy to understand**: Clear test names and documentation
- **Easy to modify**: Minimal coupling between tests
- **Realistic**: Use actual data patterns where possible
- **Fast**: Quick feedback during development

## Next Steps

1. Fix results dictionary initialization in orchestration tests
2. Adjust mock configurations for better test reliability
3. Refine PDF section parsing test expectations
4. Add integration tests for end-to-end workflows
5. Set up CI/CD integration with coverage reporting