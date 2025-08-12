# OpenRouter Setup Guide

This project uses OpenRouter to provide access to multiple AI models through a unified API. OpenRouter supports GPT-4, Claude, Llama, Gemini, and many other models.

## Getting Started

### 1. Get an OpenRouter API Key

1. Visit [OpenRouter](https://openrouter.ai/keys)
2. Sign up for an account
3. Generate an API key
4. Copy your API key

### 2. Configure Environment Variables

Copy the `.env.example` file to `.env`:

```bash
cp .env.example .env
```

Edit the `.env` file and add your OpenRouter API key:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### 3. Choose Your Model

OpenRouter supports many models. Update the `DSPY_MODEL` in your `.env` file:

#### Popular Options:

**OpenAI Models:**
- `openai/gpt-4` - GPT-4 (most capable, higher cost)
- `openai/gpt-3.5-turbo` - GPT-3.5 Turbo (fast, cost-effective)

**Anthropic Models:**
- `anthropic/claude-3-haiku` - Claude 3 Haiku (fast, affordable)
- `anthropic/claude-3-sonnet` - Claude 3 Sonnet (balanced)
- `anthropic/claude-3-opus` - Claude 3 Opus (most capable)

**Open Source Models:**
- `meta-llama/llama-3.1-8b-instruct` - Llama 3.1 8B (free tier available)
- `meta-llama/llama-3.1-70b-instruct` - Llama 3.1 70B (more capable)

**Google Models:**
- `google/gemini-pro` - Gemini Pro
- `google/gemini-flash` - Gemini Flash (faster)

### 4. Test Your Configuration

Run the test script to verify your setup:

```bash
python test_openrouter_config.py
```

### 5. Usage

Once configured, you can use the paper reviewer:

```bash
python -m martin.main "https://arxiv.org/pdf/1706.03762.pdf"
```

## Model Selection Tips

- **For development/testing**: Use `openai/gpt-3.5-turbo` or `meta-llama/llama-3.1-8b-instruct`
- **For production**: Use `openai/gpt-4` or `anthropic/claude-3-sonnet`
- **For cost optimization**: Use `anthropic/claude-3-haiku` or free tier models
- **For specific capabilities**: Check [OpenRouter Models](https://openrouter.ai/models) for detailed comparisons

## Cost Management

OpenRouter provides transparent pricing and usage tracking:

1. Monitor usage at [OpenRouter Dashboard](https://openrouter.ai/activity)
2. Set spending limits in your account settings
3. Choose models based on your budget requirements

## Troubleshooting

### Common Issues:

1. **Invalid API Key**: Ensure your key is correctly set in `.env`
2. **Model Not Found**: Check the exact model name at [OpenRouter Models](https://openrouter.ai/models)
3. **Rate Limits**: Some models have rate limits; check OpenRouter documentation
4. **Insufficient Credits**: Add credits to your OpenRouter account

### Getting Help:

- OpenRouter Documentation: https://openrouter.ai/docs
- OpenRouter Discord: https://discord.gg/openrouter
- Model Comparisons: https://openrouter.ai/models