"""Unit tests for the prompt builder service."""

import pytest

from app.services.prompt_builder import PromptBuilder


class TestPromptBuilder:
    """Test suite for PromptBuilder class."""

    @pytest.fixture
    def prompt_builder(self):
        """Create a PromptBuilder instance for testing."""
        return PromptBuilder()

    def test_initialization(self, prompt_builder):
        """Test PromptBuilder initialization."""
        assert prompt_builder.template_example is not None
        assert "CompanyName + Plaid" in prompt_builder.template_example
        assert "What You're Building" in prompt_builder.template_example

    def test_build_solution_guide_prompt_basic(self, prompt_builder):
        """Test basic solution guide prompt building."""
        transcript = "Test transcript content"
        company_name = "TestCorp"
        company_research = {
            "business_overview": "TestCorp is a fintech company",
            "technical_context": "They need API integration",
        }

        prompt = prompt_builder.build_solution_guide_prompt(
            transcript=transcript,
            company_name=company_name,
            company_research=company_research,
        )

        assert company_name in prompt
        assert transcript in prompt
        assert "TestCorp is a fintech company" in prompt
        assert "They need API integration" in prompt
        assert "INSTRUCTIONS:" in prompt
        assert "OUTPUT:" in prompt

    def test_build_solution_guide_prompt_with_context(self, prompt_builder):
        """Test solution guide prompt building with additional context."""
        transcript = "Call about payment integration"
        company_name = "FinanceApp"
        company_research = {
            "business_overview": "Finance application company",
            "technical_context": "Payment processing needs",
        }
        additional_context = "They want to integrate with Stripe"

        prompt = prompt_builder.build_solution_guide_prompt(
            transcript=transcript,
            company_name=company_name,
            company_research=company_research,
            additional_context=additional_context,
        )

        assert additional_context in prompt
        assert "They want to integrate with Stripe" in prompt

    def test_build_solution_guide_prompt_missing_research(self, prompt_builder):
        """Test prompt building with missing research data."""
        transcript = "Test transcript"
        company_name = "TestCorp"
        company_research = {}  # Empty research

        prompt = prompt_builder.build_solution_guide_prompt(
            transcript=transcript,
            company_name=company_name,
            company_research=company_research,
        )

        assert "No business overview available" in prompt
        assert "No technical context available" in prompt
        assert company_name in prompt

    def test_build_solution_guide_prompt_requirements(self, prompt_builder):
        """Test that prompt includes all required elements."""
        transcript = "Payment processing discussion"
        company_name = "PaymentCorp"
        company_research = {
            "business_overview": "Payment company",
            "technical_context": "API needs",
        }

        prompt = prompt_builder.build_solution_guide_prompt(
            transcript=transcript,
            company_name=company_name,
            company_research=company_research,
        )

        # Check for key requirements
        required_elements = [
            "expert sales engineer",
            "technical solution guides",
            "CALL TRANSCRIPT:",
            "COMPANY RESEARCH:",
            "EXAMPLE SOLUTION GUIDE STYLE:",
            "INSTRUCTIONS:",
            "KEY REQUIREMENTS:",
            "Focus on technical implementation",
            "Avoid business jargon",
            "What You're Building",
            "Core Integration",
            "Getting Started",
        ]

        for element in required_elements:
            assert element in prompt, f"Missing required element: {element}"

    def test_build_company_research_prompt(self, prompt_builder):
        """Test company research prompt building."""
        company_name = "TechStartup"
        transcript_excerpt = (
            "We're building a financial platform that needs to connect bank accounts and process payments."
        )

        prompt = prompt_builder.build_company_research_prompt(company_name, transcript_excerpt)

        assert company_name in prompt
        assert transcript_excerpt in prompt
        assert "TRANSCRIPT EXCERPT:" in prompt
        assert "What industry/sector" in prompt
        assert "business model" in prompt
        assert "technical challenges" in prompt
        assert "integration requirements" in prompt

    def test_build_company_research_prompt_format(self, prompt_builder):
        """Test company research prompt has proper format."""
        company_name = "DataCorp"
        transcript_excerpt = "Short excerpt"

        prompt = prompt_builder.build_company_research_prompt(company_name, transcript_excerpt)

        # Check structure
        assert prompt.count(company_name) >= 2  # Should appear multiple times
        assert "1. What industry" in prompt
        assert "2. What is their business" in prompt
        assert "3. What technical challenges" in prompt
        assert "4. What integration" in prompt
        assert "5. Who are their likely" in prompt

    def test_template_example_content(self, prompt_builder):
        """Test that template example contains expected content."""
        example = prompt_builder.template_example

        expected_sections = [
            "# CompanyName + Plaid // Solutions Guide",
            "## What You're Building",
            "## Core Plaid Integration",
            "### 1. Bank Account Connection",
            "### 2. Stripe Integration",
            "### 3. Transaction Data",
            "## Key Technical Details",
            "### Access Token Management",
            "### Implementation Flow",
            "## What You Get Out of the Box",
            "## Getting Started",
        ]

        for section in expected_sections:
            assert section in example, f"Missing section in example: {section}"
