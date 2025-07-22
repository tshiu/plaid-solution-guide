"""Unit tests for the main guide generator service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.guide_generator import GuideGenerator


class TestGuideGenerator:
    """Test suite for GuideGenerator class."""

    @pytest.fixture
    def guide_generator(self):
        """Create a GuideGenerator instance for testing."""
        with patch("app.services.guide_generator.GleanClient") as mock_glean:
            with patch("app.services.guide_generator.PromptBuilder") as mock_prompt:
                generator = GuideGenerator()
                generator.glean_client = mock_glean.return_value
                generator.prompt_builder = mock_prompt.return_value
                return generator

    @pytest.mark.asyncio
    async def test_generate_guide_success(self, guide_generator):
        """Test successful guide generation."""
        # Mock dependencies
        guide_generator.glean_client.get_company_insights = AsyncMock(
            return_value={
                "business_overview": "Test business overview",
                "technical_context": "Test technical context",
            }
        )
        guide_generator.glean_client.chat_query = AsyncMock(
            return_value="# TestCorp + Plaid // Solutions Guide\n\nGenerated guide content"
        )
        guide_generator.prompt_builder.build_solution_guide_prompt = MagicMock(return_value="Test prompt")

        result = await guide_generator.generate_guide(
            transcript="Test transcript",
            company_name="TestCorp",
            additional_context="Test context",
        )

        assert "TestCorp + Plaid // Solutions Guide" in result
        assert "Generated guide content" in result

    @pytest.mark.asyncio
    async def test_generate_guide_error_handling(self, guide_generator):
        """Test error handling in guide generation."""
        # Mock an error in the process
        guide_generator.glean_client.get_company_insights = AsyncMock(side_effect=Exception("Research failed"))

        with pytest.raises(Exception) as exc_info:
            await guide_generator.generate_guide(transcript="Test transcript", company_name="TestCorp")

        assert "Failed to generate solution guide" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_research_company_success(self, guide_generator):
        """Test successful company research."""
        # Mock Glean client methods
        guide_generator.glean_client.get_company_insights = AsyncMock(
            return_value={"business_overview": "Business info", "technical_context": "Tech info"}
        )
        guide_generator.glean_client.chat_query = AsyncMock(return_value="Additional research")
        guide_generator.prompt_builder.build_company_research_prompt = MagicMock(return_value="Research prompt")

        result = await guide_generator._research_company(
            company_name="TestCorp",
            transcript="Long transcript with more than 500 characters " * 10,
            additional_context="Context",
        )

        # The result should have the expected structure from get_company_insights
        assert "business_overview" in result
        assert "technical_context" in result

    @pytest.mark.asyncio
    async def test_research_company_error(self, guide_generator):
        """Test error handling in company research."""
        guide_generator.glean_client.get_company_insights = AsyncMock(side_effect=Exception("API Error"))

        result = await guide_generator._research_company(
            company_name="TestCorp",
            transcript="Test transcript",
            additional_context=None,
        )

        assert "error" in result
        assert result["company_name"] == "TestCorp"
        assert "Unable to research TestCorp" in result["business_overview"]

    def test_extract_use_case_with_context(self, guide_generator):
        """Test use case extraction with additional context."""
        transcript = "We need payment processing and bank integration for our platform."
        additional_context = "HOA financial management system"

        use_case = guide_generator._extract_use_case(transcript, additional_context)

        assert "HOA financial management system" in use_case
        assert "payment" in use_case.lower() or "bank" in use_case.lower()

    def test_extract_use_case_from_transcript(self, guide_generator):
        """Test use case extraction from transcript only."""
        transcript = """Our application needs to integrate with financial APIs.
We want to process transactions and handle payments securely."""

        use_case = guide_generator._extract_use_case(transcript, None)

        # Should contain relevant sentences with financial keywords
        assert len(use_case) > 0
        assert any(keyword in use_case.lower() for keyword in ["financial", "payment", "transaction", "api"])

    def test_extract_use_case_no_keywords(self, guide_generator):
        """Test use case extraction with no relevant keywords."""
        transcript = "We had a general conversation about the weather and sports."

        use_case = guide_generator._extract_use_case(transcript, None)

        # Should fall back to default
        assert use_case == "financial technology integration"

    def test_post_process_guide_with_title(self, guide_generator):
        """Test post-processing guide with proper title."""
        raw_guide = "# TestCorp + Plaid // Solutions Guide\n\n## What You're Building\n\nContent here"

        result = guide_generator._post_process_guide(raw_guide, "TestCorp")

        assert result.startswith("# TestCorp + Plaid // Solutions Guide")
        assert "What You're Building" in result

    def test_post_process_guide_fix_title(self, guide_generator):
        """Test post-processing guide with incorrect title."""
        raw_guide = "# Wrong Title\n\n## What You're Building\n\nContent here"

        result = guide_generator._post_process_guide(raw_guide, "TestCorp")

        assert result.startswith("# TestCorp + Plaid // Solutions Guide")

    def test_post_process_guide_add_title(self, guide_generator):
        """Test post-processing guide with missing title."""
        raw_guide = "## What You're Building\n\nContent without title"

        result = guide_generator._post_process_guide(raw_guide, "TestCorp")

        # Should add title if missing
        assert "# TestCorp + Plaid // Solutions Guide" in result

    def test_post_process_guide_cleanup(self, guide_generator):
        """Test post-processing guide cleanup."""
        raw_guide = "# TestCorp + Plaid // Solutions Guide\n\n\n\nExtra newlines\n\n\n  Trailing spaces  \n\n"

        result = guide_generator._post_process_guide(raw_guide, "TestCorp")

        # Should clean up formatting
        assert result.strip() == result  # No leading/trailing whitespace
        # Should reduce excessive newlines (but may not eliminate all triple newlines)
        assert len(result.split("\n\n\n")) <= len(raw_guide.split("\n\n\n"))

    @pytest.mark.asyncio
    async def test_validate_environment_success(self, guide_generator):
        """Test successful environment validation."""
        # Mock settings and client response
        with patch("app.config.get_settings") as mock_get_settings:
            mock_settings = MagicMock()
            mock_settings.glean_instance = "test-instance"
            mock_settings.glean_api_token = "test-token"
            mock_get_settings.return_value = mock_settings
            guide_generator.glean_client.chat_query = AsyncMock(return_value="Hello response")

            result = await guide_generator.validate_environment()

            assert result["configuration"] is True
            assert result["glean_client"] is True
            assert result["connectivity"] is True

    @pytest.mark.asyncio
    async def test_validate_environment_failure(self, guide_generator):
        """Test environment validation with failures."""
        with patch("app.config.get_settings") as mock_get_settings:
            mock_settings = MagicMock()
            mock_settings.glean_instance = ""
            mock_settings.glean_api_token = ""
            mock_get_settings.return_value = mock_settings

            result = await guide_generator.validate_environment()

            assert result["configuration"] is False
