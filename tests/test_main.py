"""
Tests for main CLI module.

Tests argument parsing, CLI interface, and main entry point functionality.
"""

import argparse
import sys
from io import StringIO
from unittest.mock import Mock, mock_open, patch

import pytest

from martin.main import cli_entry_point, main


class TestArgumentParsing:
    """Test cases for CLI argument parsing."""

    def test_argument_parser_with_minimal_args(self):
        """Test argument parser with only required arguments."""
        test_args = ["https://arxiv.org/pdf/1706.03762.pdf"]

        with patch("sys.argv", ["main.py"] + test_args):
            with patch("martin.main.config.setup_dspy_lm"):
                with patch("martin.main.PaperReviewer") as mock_reviewer:
                    with patch("martin.main.format_paper_review") as mock_format:
                        mock_reviewer_instance = Mock()
                        mock_reviewer.return_value = mock_reviewer_instance
                        mock_reviewer_instance.review.return_value = Mock(success=True)
                        mock_format.return_value = "Formatted review"

                        with patch("builtins.print") as mock_print:
                            main()

                        # Verify PaperReviewer was created with defaults
                        mock_reviewer.assert_called_once_with(
                            max_search_results=5,
                            enable_social_media=True,
                            continue_on_error=False,
                        )

                        # Verify review was called with correct URL
                        mock_reviewer_instance.review.assert_called_once_with(
                            "https://arxiv.org/pdf/1706.03762.pdf"
                        )

    def test_argument_parser_with_all_args(self):
        """Test argument parser with all possible arguments."""
        test_args = [
            "https://arxiv.org/pdf/1706.03762.pdf",
            "--output",
            "review.md",
            "--max-results",
            "10",
            "--no-social",
            "--no-toc",
            "--no-metadata",
            "--continue-on-error",
            "--verbose",
        ]

        with patch("sys.argv", ["main.py"] + test_args):
            with patch("martin.main.config.setup_dspy_lm"):
                with patch("martin.main.PaperReviewer") as mock_reviewer:
                    with patch("martin.main.format_paper_review") as mock_format:
                        with patch("builtins.open", mock_open()) as mock_file:
                            mock_reviewer_instance = Mock()
                            mock_reviewer.return_value = mock_reviewer_instance
                            mock_reviewer_instance.review.return_value = Mock(
                                success=True
                            )
                            mock_format.return_value = "Formatted review"

                            main()

                            # Verify PaperReviewer was created with custom settings
                            mock_reviewer.assert_called_once_with(
                                max_search_results=10,
                                enable_social_media=False,  # --no-social
                                continue_on_error=True,
                            )

                            # Verify format_paper_review was called with correct options
                            mock_format.assert_called_once()
                            call_args = mock_format.call_args
                            assert call_args[1]["include_toc"] is False  # --no-toc
                            assert (
                                call_args[1]["include_metadata"] is False
                            )  # --no-metadata

                            # Verify file was written (check that it was called with the output file)
                            mock_file.assert_any_call(
                                "review.md", "w", encoding="utf-8"
                            )

    def test_argument_parser_short_options(self):
        """Test argument parser with short option flags."""
        test_args = ["https://arxiv.org/pdf/1706.03762.pdf", "-o", "output.md", "-v"]

        with patch("sys.argv", ["main.py"] + test_args):
            with patch("martin.main.config.setup_dspy_lm"):
                with patch("martin.main.PaperReviewer") as mock_reviewer:
                    with patch("martin.main.format_paper_review") as mock_format:
                        with patch("builtins.open", mock_open()):
                            mock_reviewer_instance = Mock()
                            mock_reviewer.return_value = mock_reviewer_instance
                            mock_reviewer_instance.review.return_value = Mock(
                                success=True
                            )
                            mock_format.return_value = "Formatted review"

                            main()

                            # Should work the same as long options
                            mock_reviewer.assert_called_once()

    def test_argument_parser_invalid_max_results(self):
        """Test argument parser with invalid max-results value."""
        test_args = [
            "https://arxiv.org/pdf/1706.03762.pdf",
            "--max-results",
            "not-a-number",
        ]

        with patch("sys.argv", ["main.py"] + test_args):
            with pytest.raises(SystemExit):
                main()

    def test_argument_parser_missing_required_arg(self):
        """Test argument parser with missing required PDF URL."""
        test_args = ["--verbose"]  # Missing PDF URL

        with patch("sys.argv", ["main.py"] + test_args):
            with pytest.raises(SystemExit):
                main()

    def test_argument_parser_help_text(self):
        """Test that help text is properly formatted."""
        test_args = ["--help"]

        with patch("sys.argv", ["main.py"] + test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()

            # Help should exit with code 0
            assert exc_info.value.code == 0

    def test_help_text_includes_martin_branding(self):
        """Test that help text includes Martin's friendly branding."""
        test_args = ["--help"]

        with patch("sys.argv", ["main.py"] + test_args):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                with pytest.raises(SystemExit):
                    main()

                # Should include Martin's friendly introduction in help
                help_output = mock_stdout.getvalue()
                assert (
                    "Hi! I'm Martin, your friendly research paper reviewer buddy"
                    in help_output
                )
                assert (
                    "Just give me a paper URL and I'll provide you with a comprehensive, friendly review!"
                    in help_output
                )
                assert "🤓" in help_output


class TestMainExecution:
    """Test cases for main execution flow."""

    @patch("martin.main.load_dotenv")
    @patch("martin.main.config.setup_dspy_lm")
    @patch("martin.main.PaperReviewer")
    @patch("martin.main.format_paper_review")
    def test_main_successful_execution(
        self, mock_format, mock_reviewer, mock_setup, mock_load_dotenv
    ):
        """Test successful main execution flow."""
        test_args = ["https://arxiv.org/pdf/1706.03762.pdf"]

        # Setup mocks
        mock_reviewer_instance = Mock()
        mock_reviewer.return_value = mock_reviewer_instance
        mock_result = Mock(success=True, errors=[], warnings=[])
        mock_reviewer_instance.review.return_value = mock_result
        mock_format.return_value = "Formatted review content"

        with patch("sys.argv", ["main.py"] + test_args):
            with patch("builtins.print") as mock_print:
                main()

        # Verify execution flow
        mock_load_dotenv.assert_called_once()
        mock_setup.assert_called_once()
        mock_reviewer.assert_called_once()
        mock_reviewer_instance.review.assert_called_once_with(
            "https://arxiv.org/pdf/1706.03762.pdf"
        )
        mock_format.assert_called_once()
        mock_print.assert_called_with("Formatted review content")

    @patch("martin.main.load_dotenv")
    @patch("martin.main.config.setup_dspy_lm")
    @patch("martin.main.PaperReviewer")
    @patch("martin.main.format_paper_review")
    def test_main_with_file_output(
        self, mock_format, mock_reviewer, mock_setup, mock_load_dotenv
    ):
        """Test main execution with file output."""
        test_args = [
            "https://arxiv.org/pdf/1706.03762.pdf",
            "--output",
            "test_output.md",
        ]

        # Setup mocks
        mock_reviewer_instance = Mock()
        mock_reviewer.return_value = mock_reviewer_instance
        mock_result = Mock(success=True)
        mock_reviewer_instance.review.return_value = mock_result
        mock_format.return_value = "Formatted review content"

        with patch("sys.argv", ["main.py"] + test_args):
            with patch("builtins.open", mock_open()) as mock_file:
                with patch("builtins.print") as mock_print:
                    main()

        # Verify file was opened and written
        mock_file.assert_called_once_with("test_output.md", "w", encoding="utf-8")
        mock_file().write.assert_called_once_with("Formatted review content")
        mock_print.assert_called_with("📄 Review saved to: test_output.md")

    @patch("martin.main.load_dotenv")
    @patch("martin.main.config.setup_dspy_lm")
    def test_main_configuration_error(self, mock_setup, mock_load_dotenv):
        """Test main execution with configuration error."""
        test_args = ["https://arxiv.org/pdf/1706.03762.pdf"]

        # Mock configuration error
        mock_setup.side_effect = ValueError("Configuration error: Missing API key")

        with patch("sys.argv", ["main.py"] + test_args):
            with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
                with pytest.raises(SystemExit) as exc_info:
                    main()

                # Should exit with code 1
                assert exc_info.value.code == 1

                # Should print Martin's friendly error to stderr
                stderr_output = mock_stderr.getvalue()
                assert "😅 Oops! I had trouble getting set up:" in stderr_output

    @patch("martin.main.load_dotenv")
    @patch("martin.main.config.setup_dspy_lm")
    @patch("martin.main.PaperReviewer")
    def test_main_keyboard_interrupt(self, mock_reviewer, mock_setup, mock_load_dotenv):
        """Test main execution with keyboard interrupt."""
        test_args = ["https://arxiv.org/pdf/1706.03762.pdf"]

        # Mock keyboard interrupt during review
        mock_reviewer_instance = Mock()
        mock_reviewer.return_value = mock_reviewer_instance
        mock_reviewer_instance.review.side_effect = KeyboardInterrupt()

        with patch("sys.argv", ["main.py"] + test_args):
            with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
                with pytest.raises(SystemExit) as exc_info:
                    main()

                # Should exit with code 1
                assert exc_info.value.code == 1

                # Should print Martin's friendly interrupt message
                stderr_output = mock_stderr.getvalue()
                assert (
                    "No worries! Thanks for letting me know you wanted to stop"
                    in stderr_output
                )

    @patch("martin.main.load_dotenv")
    @patch("martin.main.config.setup_dspy_lm")
    @patch("martin.main.PaperReviewer")
    def test_main_generic_exception(self, mock_reviewer, mock_setup, mock_load_dotenv):
        """Test main execution with generic exception."""
        test_args = ["https://arxiv.org/pdf/1706.03762.pdf"]

        # Mock generic exception during review
        mock_reviewer_instance = Mock()
        mock_reviewer.return_value = mock_reviewer_instance
        mock_reviewer_instance.review.side_effect = Exception(
            "Unexpected error occurred"
        )

        with patch("sys.argv", ["main.py"] + test_args):
            with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
                with pytest.raises(SystemExit) as exc_info:
                    main()

                # Should exit with code 1
                assert exc_info.value.code == 1

                # Should print Martin's friendly error message
                stderr_output = mock_stderr.getvalue()
                assert (
                    "Oh no! I ran into an unexpected hiccup: Unexpected error occurred"
                    in stderr_output
                )


class TestVerboseMode:
    """Test cases for verbose mode functionality."""

    @patch("martin.main.load_dotenv")
    @patch("martin.main.config.setup_dspy_lm")
    @patch("martin.main.PaperReviewer")
    @patch("martin.main.format_paper_review")
    @patch("martin.main.time.time")
    def test_verbose_mode_output(
        self, mock_time, mock_format, mock_reviewer, mock_setup, mock_load_dotenv
    ):
        """Test verbose mode produces additional output."""
        test_args = ["https://arxiv.org/pdf/1706.03762.pdf", "--verbose"]

        # Mock time for duration calculation
        mock_time.side_effect = [1000.0, 1005.5]  # 5.5 second duration

        # Setup mocks
        mock_reviewer_instance = Mock()
        mock_reviewer.return_value = mock_reviewer_instance
        mock_result = Mock(success=True, errors=[], warnings=[])
        mock_reviewer_instance.review.return_value = mock_result
        mock_format.return_value = "Formatted review"

        with patch("sys.argv", ["main.py"] + test_args):
            with patch("builtins.print") as mock_print:
                main()

        # Verify verbose output was printed
        print_calls = [call[0][0] for call in mock_print.call_args_list]

        # Should include setup messages
        assert any("Let me just get my thinking cap on" in call for call in print_calls)
        assert any(
            "All set! Ready to explore some fascinating research" in call
            for call in print_calls
        )
        assert any("Now let's take a look at" in call for call in print_calls)
        assert any(
            "Finished my analysis in 5.5 seconds" in call for call in print_calls
        )
        assert any(
            "Now let me put together my thoughts for you" in call
            for call in print_calls
        )
        assert any(
            "All done! I hope you found my review helpful" in call
            for call in print_calls
        )

    @patch("martin.main.load_dotenv")
    @patch("martin.main.config.setup_dspy_lm")
    @patch("martin.main.PaperReviewer")
    @patch("martin.main.format_paper_review")
    def test_verbose_mode_with_errors(
        self, mock_format, mock_reviewer, mock_setup, mock_load_dotenv
    ):
        """Test verbose mode with errors and warnings."""
        test_args = ["https://arxiv.org/pdf/1706.03762.pdf", "--verbose"]

        # Setup mocks with errors
        mock_reviewer_instance = Mock()
        mock_reviewer.return_value = mock_reviewer_instance
        mock_result = Mock(
            success=False, errors=["Error 1", "Error 2"], warnings=["Warning 1"]
        )
        mock_reviewer_instance.review.return_value = mock_result
        mock_format.return_value = "Formatted review"

        with patch("sys.argv", ["main.py"] + test_args):
            with patch("builtins.print") as mock_print:
                main()

        # Verify error summary was printed
        print_calls = [call[0][0] for call in mock_print.call_args_list]

        assert any(
            "I finished the review, but ran into a few bumps along the way" in call
            for call in print_calls
        )
        assert any(
            "I encountered 2 issue(s) - but kept going" in call for call in print_calls
        )
        assert any("There were 1 thing(s) worth noting" in call for call in print_calls)

    @patch("martin.main.load_dotenv")
    @patch("martin.main.config.setup_dspy_lm")
    def test_verbose_mode_configuration_error(self, mock_setup, mock_load_dotenv):
        """Test verbose mode with configuration error."""
        test_args = ["https://arxiv.org/pdf/1706.03762.pdf", "--verbose"]

        # Mock configuration error
        mock_setup.side_effect = ValueError("Missing API key")

        with patch("sys.argv", ["main.py"] + test_args):
            with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
                with pytest.raises(SystemExit):
                    main()

                # Should include helpful hint in verbose mode
                stderr_output = mock_stderr.getvalue()
                assert (
                    "This usually means I need my OpenRouter API key configured properly"
                    in stderr_output
                )


class TestFileHandling:
    """Test cases for file output handling."""

    @patch("martin.main.load_dotenv")
    @patch("martin.main.config.setup_dspy_lm")
    @patch("martin.main.PaperReviewer")
    @patch("martin.main.format_paper_review")
    def test_file_output_success(
        self, mock_format, mock_reviewer, mock_setup, mock_load_dotenv
    ):
        """Test successful file output."""
        test_args = ["https://arxiv.org/pdf/1706.03762.pdf", "--output", "test.md"]

        # Setup mocks
        mock_reviewer_instance = Mock()
        mock_reviewer.return_value = mock_reviewer_instance
        mock_reviewer_instance.review.return_value = Mock(success=True)
        mock_format.return_value = "Review content"

        with patch("sys.argv", ["main.py"] + test_args):
            with patch("builtins.open", mock_open()) as mock_file:
                with patch("builtins.print") as mock_print:
                    main()

        # Verify file operations
        mock_file.assert_called_once_with("test.md", "w", encoding="utf-8")
        mock_file().write.assert_called_once_with("Review content")
        mock_print.assert_called_with("📄 Review saved to: test.md")

    @patch("martin.main.load_dotenv")
    @patch("martin.main.config.setup_dspy_lm")
    @patch("martin.main.PaperReviewer")
    @patch("martin.main.format_paper_review")
    def test_file_output_permission_error(
        self, mock_format, mock_reviewer, mock_setup, mock_load_dotenv
    ):
        """Test file output with permission error."""
        test_args = [
            "https://arxiv.org/pdf/1706.03762.pdf",
            "--output",
            "/root/test.md",
        ]

        # Setup mocks
        mock_reviewer_instance = Mock()
        mock_reviewer.return_value = mock_reviewer_instance
        mock_reviewer_instance.review.return_value = Mock(success=True)
        mock_format.return_value = "Review content"

        with patch("sys.argv", ["main.py"] + test_args):
            with patch(
                "builtins.open", side_effect=PermissionError("Permission denied")
            ):
                with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
                    with pytest.raises(SystemExit):
                        main()

                    # Should handle file permission error
                    stderr_output = mock_stderr.getvalue()
                    assert "Oh no! I ran into an unexpected hiccup:" in stderr_output


class TestCLIEntryPoint:
    """Test cases for CLI entry point function."""

    @patch("martin.main.main")
    def test_cli_entry_point(self, mock_main):
        """Test CLI entry point calls main function."""
        cli_entry_point()
        mock_main.assert_called_once()

    @patch("martin.main.main")
    def test_cli_entry_point_with_exception(self, mock_main):
        """Test CLI entry point handles exceptions from main."""
        mock_main.side_effect = Exception("Test exception")

        # Should not raise exception, main should handle it
        with pytest.raises(Exception):
            cli_entry_point()


class TestMartinBranding:
    """Test cases for Martin branding and personality in CLI output."""

    @patch("martin.main.load_dotenv")
    @patch("martin.main.config.setup_dspy_lm")
    @patch("martin.main.PaperReviewer")
    @patch("martin.main.format_paper_review")
    def test_martin_greeting_in_verbose_mode(
        self, mock_format, mock_reviewer, mock_setup, mock_load_dotenv
    ):
        """Test that Martin's greeting appears in verbose mode."""
        test_args = ["https://arxiv.org/pdf/1706.03762.pdf", "--verbose"]

        # Setup mocks
        mock_reviewer_instance = Mock()
        mock_reviewer.return_value = mock_reviewer_instance
        mock_result = Mock(success=True, errors=[], warnings=[])
        mock_reviewer_instance.review.return_value = mock_result
        mock_format.return_value = "Formatted review"

        with patch("sys.argv", ["main.py"] + test_args):
            with patch("builtins.print") as mock_print:
                main()

        # Verify Martin's friendly messages appear
        print_calls = [call[0][0] for call in mock_print.call_args_list]

        # Should include Martin's setup greeting
        assert any("Let me just get my thinking cap on" in call for call in print_calls)
        assert any(
            "All set! Ready to explore some fascinating research" in call
            for call in print_calls
        )

        # Should include Martin's working messages
        assert any("Now let's take a look at" in call for call in print_calls)
        assert any(
            "Now let me put together my thoughts for you" in call
            for call in print_calls
        )

        # Should include Martin's completion message
        assert any(
            "All done! I hope you found my review helpful" in call
            for call in print_calls
        )

    @patch("martin.main.load_dotenv")
    @patch("martin.main.config.setup_dspy_lm")
    @patch("martin.main.PaperReviewer")
    @patch("martin.main.format_paper_review")
    def test_martin_personality_in_error_messages(
        self, mock_format, mock_reviewer, mock_setup, mock_load_dotenv
    ):
        """Test that Martin's personality comes through in error messages."""
        test_args = ["https://arxiv.org/pdf/1706.03762.pdf"]

        # Mock generic exception during review
        mock_reviewer_instance = Mock()
        mock_reviewer.return_value = mock_reviewer_instance
        mock_reviewer_instance.review.side_effect = Exception("Test error")

        with patch("sys.argv", ["main.py"] + test_args):
            with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
                with pytest.raises(SystemExit):
                    main()

                # Should include Martin's friendly error message
                stderr_output = mock_stderr.getvalue()
                assert "Oh no! I ran into an unexpected hiccup:" in stderr_output

    @patch("martin.main.load_dotenv")
    @patch("martin.main.config.setup_dspy_lm")
    @patch("martin.main.PaperReviewer")
    @patch("martin.main.format_paper_review")
    def test_martin_file_output_message(
        self, mock_format, mock_reviewer, mock_setup, mock_load_dotenv
    ):
        """Test that Martin's personality appears in file output messages."""
        test_args = ["https://arxiv.org/pdf/1706.03762.pdf", "--output", "test.md"]

        # Setup mocks
        mock_reviewer_instance = Mock()
        mock_reviewer.return_value = mock_reviewer_instance
        mock_reviewer_instance.review.return_value = Mock(success=True)
        mock_format.return_value = "Review content"

        with patch("sys.argv", ["main.py"] + test_args):
            with patch("builtins.open", mock_open()) as mock_file:
                with patch("builtins.print") as mock_print:
                    main()

        # Should include Martin's friendly file save message
        mock_print.assert_called_with("📄 Review saved to: test.md")

    @patch("martin.main.load_dotenv")
    @patch("martin.main.config.setup_dspy_lm")
    @patch("martin.main.PaperReviewer")
    @patch("martin.main.format_paper_review")
    def test_martin_encouragement_with_errors(
        self, mock_format, mock_reviewer, mock_setup, mock_load_dotenv
    ):
        """Test that Martin provides encouragement even when there are errors."""
        test_args = ["https://arxiv.org/pdf/1706.03762.pdf", "--verbose"]

        # Setup mocks with errors
        mock_reviewer_instance = Mock()
        mock_reviewer.return_value = mock_reviewer_instance
        mock_result = Mock(
            success=False,
            errors=["Test error 1", "Test error 2"],
            warnings=["Test warning"],
        )
        mock_reviewer_instance.review.return_value = mock_result
        mock_format.return_value = "Formatted review"

        with patch("sys.argv", ["main.py"] + test_args):
            with patch("builtins.print") as mock_print:
                main()

        # Verify Martin's encouraging error summary
        print_calls = [call[0][0] for call in mock_print.call_args_list]

        assert any(
            "I finished the review, but ran into a few bumps along the way" in call
            for call in print_calls
        )
        assert any(
            "I encountered 2 issue(s) - but kept going" in call for call in print_calls
        )
        assert any("There were 1 thing(s) worth noting" in call for call in print_calls)


class TestArgumentValidation:
    """Test cases for argument validation and edge cases."""

    def test_pdf_url_argument_validation(self):
        """Test that PDF URL argument is properly captured."""
        test_url = "https://example.com/paper.pdf"
        test_args = [test_url]

        with patch("sys.argv", ["main.py"] + test_args):
            with patch("martin.main.config.setup_dspy_lm"):
                with patch("martin.main.PaperReviewer") as mock_reviewer:
                    with patch("martin.main.format_paper_review"):
                        with patch("builtins.print"):
                            mock_reviewer_instance = Mock()
                            mock_reviewer.return_value = mock_reviewer_instance
                            mock_reviewer_instance.review.return_value = Mock(
                                success=True
                            )

                            main()

                            # Verify URL was passed correctly
                            mock_reviewer_instance.review.assert_called_once_with(
                                test_url
                            )

    def test_max_results_type_conversion(self):
        """Test that max-results argument is converted to integer."""
        test_args = ["https://example.com/paper.pdf", "--max-results", "15"]

        with patch("sys.argv", ["main.py"] + test_args):
            with patch("martin.main.config.setup_dspy_lm"):
                with patch("martin.main.PaperReviewer") as mock_reviewer:
                    with patch("martin.main.format_paper_review"):
                        with patch("builtins.print"):
                            mock_reviewer_instance = Mock()
                            mock_reviewer.return_value = mock_reviewer_instance
                            mock_reviewer_instance.review.return_value = Mock(
                                success=True
                            )

                            main()

                            # Verify integer conversion
                            mock_reviewer.assert_called_once_with(
                                max_search_results=15,  # Should be integer
                                enable_social_media=True,
                                continue_on_error=False,
                            )

    def test_boolean_flag_handling(self):
        """Test that boolean flags are handled correctly."""
        test_args = [
            "https://example.com/paper.pdf",
            "--no-social",
            "--continue-on-error",
        ]

        with patch("sys.argv", ["main.py"] + test_args):
            with patch("martin.main.config.setup_dspy_lm"):
                with patch("martin.main.PaperReviewer") as mock_reviewer:
                    with patch("martin.main.format_paper_review"):
                        with patch("builtins.print"):
                            mock_reviewer_instance = Mock()
                            mock_reviewer.return_value = mock_reviewer_instance
                            mock_reviewer_instance.review.return_value = Mock(
                                success=True
                            )

                            main()

                            # Verify boolean flags
                            mock_reviewer.assert_called_once_with(
                                max_search_results=5,
                                enable_social_media=False,  # --no-social
                                continue_on_error=True,  # --continue-on-error
                            )
