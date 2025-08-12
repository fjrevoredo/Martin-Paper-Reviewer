"""
Data model for structured paper text content.

Represents extracted and parsed text from research papers with
clearly defined sections.
"""

from typing import Optional

from pydantic import BaseModel, Field


class PaperText(BaseModel):
    """
    Structured representation of research paper text content.

    Contains the full text and parsed sections for easy access
    to different parts of the paper during analysis.
    """

    full_text: str = Field(description="Complete extracted text from the PDF")

    abstract: str = Field(default="", description="Paper abstract or summary section")

    introduction: str = Field(default="", description="Introduction section content")

    methodology: str = Field(
        default="", description="Methodology, methods, or approach section"
    )

    results: str = Field(
        default="", description="Results, findings, or experiments section"
    )

    conclusion: str = Field(
        default="", description="Conclusion, discussion, or future work section"
    )

    references: str = Field(
        default="", description="References or bibliography section"
    )

    def has_section(self, section_name: str) -> bool:
        """
        Check if a specific section has content.

        Args:
            section_name: Name of the section to check

        Returns:
            True if section exists and has content
        """
        section_content = getattr(self, section_name, "")
        if section_content is None:
            return False
        return bool(section_content.strip())

    def get_section_summary(self) -> dict:
        """
        Get a summary of which sections were successfully extracted.

        Returns:
            Dictionary mapping section names to boolean availability
        """
        sections = [
            "abstract",
            "introduction",
            "methodology",
            "results",
            "conclusion",
            "references",
        ]
        return {section: self.has_section(section) for section in sections}

    def get_main_content(self) -> str:
        """
        Get the main content sections (excluding references).

        Returns:
            Combined text of main content sections
        """
        main_sections = []

        if self.has_section("abstract"):
            main_sections.append(f"Abstract:\n{self.abstract}")

        if self.has_section("introduction"):
            main_sections.append(f"Introduction:\n{self.introduction}")

        if self.has_section("methodology"):
            main_sections.append(f"Methodology:\n{self.methodology}")

        if self.has_section("results"):
            main_sections.append(f"Results:\n{self.results}")

        if self.has_section("conclusion"):
            main_sections.append(f"Conclusion:\n{self.conclusion}")

        return "\n\n".join(main_sections) if main_sections else self.full_text
