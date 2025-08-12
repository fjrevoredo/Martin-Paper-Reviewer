"""
Martin - Your friendly research paper reviewer buddy

Provides a conversational command-line interface for reviewing research papers.
"""

import argparse
import sys
import time

from dotenv import load_dotenv

from .config import config
from .formatter import format_paper_review
from .paper_reviewer import PaperReviewer


def main():
    """Main CLI entry point."""
    # Load environment variables from .env file
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Hi! I'm Martin, your friendly research paper reviewer buddy. 🤓\nJust give me a paper URL and I'll provide you with a comprehensive, friendly review!",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  martin https://arxiv.org/pdf/1706.03762.pdf
  martin https://arxiv.org/pdf/1706.03762.pdf -o review.md --verbose
  martin https://arxiv.org/pdf/1706.03762.pdf --no-social --max-results 3
        """,
    )

    parser.add_argument(
        "pdf_url", help="The URL or path to the research paper you'd like me to review"
    )

    parser.add_argument(
        "--output",
        "-o",
        help="Save my review to a file instead of showing it here",
        default=None,
    )

    parser.add_argument(
        "--max-results",
        type=int,
        default=5,
        help="How many related papers should I look at for comparison? (default: 5)",
    )

    parser.add_argument(
        "--no-social",
        action="store_true",
        help="Skip creating social media content (I won't generate tweets/posts)",
    )

    parser.add_argument(
        "--no-toc",
        action="store_true",
        help="Skip the table of contents (go straight to my review)",
    )

    parser.add_argument(
        "--no-metadata",
        action="store_true",
        help="Skip the technical details (just show my main review)",
    )

    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        default=False,
        help="Keep going even if I run into some trouble along the way",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Let me tell you what I'm thinking as I work through the paper",
    )

    args = parser.parse_args()

    # Martin's greeting
    if args.verbose:
        print("👋 Hey there! I'm Martin, your research paper reviewer buddy!")
        print("🤓 I'm excited to dive into this paper with you!")
    else:
        print("👋 Hi! I'm Martin - let me review that paper for you...")

    try:
        # Setup DSPy language model
        if args.verbose:
            print("🔧 Let me just get my thinking cap on...")

        config.setup_dspy_lm()

        if args.verbose:
            print("✅ All set! Ready to explore some fascinating research!")
            print(f"📄 Now let's take a look at: {args.pdf_url}")
            print("⏳ This might take a few minutes - I like to be thorough! ☕")

        # Initialize PaperReviewer
        reviewer = PaperReviewer(
            max_search_results=args.max_results,
            enable_social_media=not args.no_social,
            continue_on_error=args.continue_on_error,
        )

        # Start timing
        start_time = time.time()

        # Execute review
        result = reviewer.review(args.pdf_url)

        # Calculate duration
        duration = time.time() - start_time

        if args.verbose:
            print(f"⏱️ Finished my analysis in {duration:.1f} seconds!")
            print("📝 Now let me put together my thoughts for you...")

        # Format output
        formatted_review = format_paper_review(
            result,
            args.pdf_url,
            include_toc=not args.no_toc,
            include_metadata=not args.no_metadata,
        )

        # Output results
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(formatted_review)

            if args.verbose:
                print(f"✅ Perfect! I've saved my review to: {args.output}")
            else:
                print(f"📄 Review saved to: {args.output}")
        else:
            print(formatted_review)

        # Show summary
        if args.verbose and hasattr(result, "success"):
            if result.success:
                print("🎉 All done! I hope you found my review helpful!")
                print("💡 Feel free to ask me to review another paper anytime!")
            else:
                print(
                    "😅 I finished the review, but ran into a few bumps along the way"
                )
                if hasattr(result, "errors") and result.errors:
                    print(
                        f"   I encountered {len(result.errors)} issue(s) - but kept going!"
                    )
                if hasattr(result, "warnings") and result.warnings:
                    print(f"   There were {len(result.warnings)} thing(s) worth noting")

    except ValueError as e:
        print(f"😅 Oops! I had trouble getting set up: {e}", file=sys.stderr)
        if args.verbose:
            print(
                "💡 This usually means I need my OpenRouter API key configured properly.",
                file=sys.stderr,
            )
            print(
                "   Check your .env file and make sure OPENROUTER_API_KEY is set!",
                file=sys.stderr,
            )
        else:
            print(
                "💡 Try running with --verbose to see what I need help with!",
                file=sys.stderr,
            )
        sys.exit(1)
    except KeyboardInterrupt:
        print(
            "\n👋 No worries! Thanks for letting me know you wanted to stop.",
            file=sys.stderr,
        )
        print(
            "Feel free to come back anytime - I'll be here when you need me! 🤓",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as e:
        print(f"😔 Oh no! I ran into an unexpected hiccup: {e}", file=sys.stderr)
        print(
            "This definitely isn't your fault - something went sideways on my end. Let's try again!",
            file=sys.stderr,
        )
        if args.verbose:
            print("Here are the technical details in case they help:", file=sys.stderr)
            import traceback

            traceback.print_exc()
        else:
            print(
                "💡 Try running with --verbose if you'd like to see more details!",
                file=sys.stderr,
            )
        sys.exit(1)


def cli_entry_point():
    """Entry point for console script."""
    main()


if __name__ == "__main__":
    main()
