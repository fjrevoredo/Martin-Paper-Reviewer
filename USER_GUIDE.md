# 🤓 Martin User Guide - Let's Review Some Papers Together!

Hey there! I'm Martin, and I'm excited to help you understand research papers better. This guide will walk you through everything you need to know about working with me.

## Getting to Know Martin

I'm your friendly research paper reviewer buddy. Think of me as that knowledgeable friend who loves diving deep into academic papers and explaining them in plain English. I don't just summarize papers - I analyze them, critique them, and help you understand their place in the broader research landscape.

## What Makes Me Different

Unlike other paper analysis tools, I:
- **Talk like a human**: No robotic responses here - I'll chat with you about the research
- **Give honest opinions**: If a paper has problems, I'll tell you (but nicely!)
- **Explain the context**: I'll show you how this paper fits with other research
- **Keep it real**: I use conversational language while maintaining scientific accuracy

## Quick Start Guide

### 1. First Time Setup

Before we can work together, you'll need to set up your environment. For detailed installation and configuration instructions, please see the [README.md](README.md) file.

### 2. Your First Review

Let's start with something simple:

```bash
martin https://arxiv.org/pdf/1706.03762.pdf
```

I'll download the paper, read through it, and give you my thoughts. The whole process takes a few minutes, and I'll keep you updated on what I'm doing.

### 3. Saving My Reviews

Want to keep my review for later? Just tell me where to save it:

```bash
martin https://arxiv.org/pdf/1706.03762.pdf -o my_review.md
```

## Understanding My Review Process

I follow an 8-step process to analyze papers thoroughly:

### 📄 Step 1: Reading the Paper
I start by carefully extracting and parsing the PDF content. I'll identify different sections and understand the paper's structure.

### 📋 Step 2: Getting the Basics
I extract key information like title, authors, abstract, and keywords. Think of this as getting my bearings.

### 🔬 Step 3: Methodology Deep-Dive
This is where I really dig in. I analyze:
- How well the methods are explained
- Whether the experiments are well-designed
- How reproducible the work is (I give it a score from 1-10)
- What the strengths and weaknesses are

### 💡 Step 4: Contribution Analysis
I evaluate what's genuinely new and important about this research:
- What are the main contributions?
- How novel are they really?
- How significant is the impact?

### 📚 Step 5: Literature Context
I search through arXiv and Semantic Scholar to find related papers and see how this work fits in:
- What similar work exists?
- How does this paper compare?
- What's the broader context?

### 📊 Step 6: Impact Assessment
I predict how this research might influence:
- The academic field
- Real-world applications
- Future research directions

### ⭐ Step 7: Final Verdict
I give you my honest recommendation using a 5-level system:
- **Highly Recommended**: This is excellent work that advances the field
- **Worth Reading**: Good paper with solid contributions
- **Mixed**: Has merit but also significant limitations
- **Not Recommended**: Serious flaws or limited contribution
- **Avoid**: Major problems that undermine the work

### 📱 Step 8: Social Media Content (Optional)
For papers I really like, I'll create social media content you can use to share the research.

## Customizing How I Work

### Verbose Mode (My Favorite!)
Use `--verbose` and I'll tell you exactly what I'm thinking as I work:

```bash
martin paper.pdf --verbose
```

You'll see messages like:
- "📄 Hey! I'm grabbing that paper for you..."
- "🔍 Now I'm diving into the methodology - this looks interesting!"
- "📊 Almost done! Just putting together my thoughts..."

### Literature Search Options
Control how many related papers I find:

```bash
# Find more papers for comparison (default is 5 from each source)
martin paper.pdf --max-results 10

# Skip social media content generation
martin paper.pdf --no-social
```

### Output Customization
```bash
# Skip table of contents
martin paper.pdf --no-toc

# Skip metadata
martin paper.pdf --no-metadata

# Continue even if I hit problems (I usually stop to let you know what's wrong)
martin paper.pdf --continue-on-error
```

## Tips for Getting the Best Reviews

### 1. Paper Quality Matters
I work best with:
- Well-structured PDFs with clear sections
- Papers with proper abstracts and conclusions
- Research with clear methodology descriptions

### 2. Internet Connection
I need internet access to:
- Download papers from URLs
- Search academic databases
- Access the AI models that power my thinking

### 3. Model Selection
I work best with:
- `openai/gpt-4` (premium quality)
- `openai/gpt-4o-mini` (great balance - my personal favorite)
- `openai/gpt-3.5-turbo` (fast and budget-friendly)

### 4. API Limits
If you're doing lots of reviews, consider:
- Getting a Semantic Scholar API key for better literature search
- Monitoring your OpenRouter usage
- Using `--max-results` to control search scope

## Troubleshooting Common Issues

### "I can't download that paper"
- Check if the URL is correct and accessible
- Some papers might be behind paywalls
- Try downloading the PDF manually and using a local file path

### "Model compatibility error"
- Make sure you're using a supported model (see MODEL_COMPATIBILITY.md)
- Check your API key is valid
- Try switching to `openai/gpt-4o-mini`

### "Literature search failed"
- This usually means the academic APIs are having issues
- I'll continue with the review using just the paper content
- Try again later or use `--continue-on-error`

### "PDF parsing failed"
- Some PDFs are tricky to parse
- Try a different version of the paper
- Check if the PDF is corrupted

## Advanced Usage

### Batch Processing
Want to review multiple papers? You can script it:

```bash
# Review multiple papers
for paper in paper1.pdf paper2.pdf paper3.pdf; do
    martin "$paper" -o "review_$(basename "$paper" .pdf).md"
done
```

### Custom Configuration
Set up your `.env` file for optimal performance:

```bash
# Your OpenRouter API key
OPENROUTER_API_KEY=your_key_here

# Preferred model
DSPY_MODEL=openai/gpt-4o-mini

# Temperature for creativity (0.0-1.0, I prefer 0.1 for consistency)
DSPY_TEMPERATURE=0.1

# Optional: Semantic Scholar API key for better literature search
SEMANTIC_SCHOLAR_API_KEY=your_key_here

# Maximum papers to find for literature comparison
LITERATURE_MAX_RESULTS=10
```

## Getting Help

### If Something Goes Wrong
I try to give helpful error messages, but if you're stuck:
1. Check this guide first
2. Look at the README.md for setup issues
3. Check MODEL_COMPATIBILITY.md for model issues
4. Open an issue on GitHub if you think it's a bug

### Feature Requests
Got an idea for how I could be better? I'd love to hear it! Open a GitHub issue or discussion.

### Contributing
Want to help make me better? Check out CONTRIBUTING.md for guidelines on:
- Code contributions
- Documentation improvements
- Bug reports
- Feature suggestions

## Final Thoughts

I'm here to make research paper analysis more accessible and enjoyable. Don't hesitate to experiment with different options and see what works best for your workflow.

Remember: I'm designed to be helpful, honest, and friendly. If you ever feel like I'm being too technical or not clear enough, that's feedback I'd love to hear!

Happy paper reviewing! 🤓

---

*Questions? Issues? Ideas? I'd love to hear from you through GitHub issues or discussions!*