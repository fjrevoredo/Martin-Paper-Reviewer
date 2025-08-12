# Martin - Model Compatibility Guide

This document lists the compatibility status of various OpenRouter models with Martin.

## ✅ Fully Compatible Models

These models work perfectly with all features of Martin:

- `openai/gpt-4` - GPT-4 (Recommended for best quality)
- `openai/gpt-4o-mini` - GPT-4o Mini (Recommended for speed/cost balance)
- `openai/gpt-3.5-turbo` - GPT-3.5 Turbo (Fastest, good quality)

## ❌ Incompatible Models

These models do not work with Martin due to various limitations:

### Models without structured output support:
- `anthropic/claude-3-haiku` - No structured output support
- `anthropic/claude-3-sonnet` - No structured output support

### Models with provider issues:
- `meta-llama/llama-3.1-8b-instruct` - LLM Provider configuration issues
- `meta-llama/llama-3.1-70b-instruct` - LLM Provider configuration issues
- `google/gemini-pro` - LLM Provider configuration issues
- `mistralai/mistral-7b-instruct` - LLM Provider configuration issues


## Configuration

To use a compatible model, update your `.env` file:

```env
DSPY_MODEL=openai/gpt-3.5-turbo
```
## Recommendations

For best results, use one of the fully compatible OpenAI models:

- **For production**: `openai/gpt-4` (highest quality)
- **For development**: `openai/gpt-4o-mini` (good balance of speed and quality)
- **For testing**: `openai/gpt-3.5-turbo` (fastest and most cost-effective)

## Testing New Models

To test if a new model works with Martin:

1. Update your `.env` file with the model name
2. Run: `python -m martin --help`
3. If the configuration step passes, the model should work
4. If it fails, you'll get a clear error message explaining why

The application is designed to fail fast with clear error messages rather than continue with degraded functionality.