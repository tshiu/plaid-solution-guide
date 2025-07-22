"""Main service for generating solution guides from transcripts."""

import logging
from typing import Any

from app.services.glean_client import GleanClient
from app.services.prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)


class GuideGenerator:
    """Main service for generating solution guides from call transcripts.

    This service orchestrates the entire process of:
    1. Researching the company using Glean APIs
    2. Building sophisticated prompts
    3. Generating solution guides using the company's LLM capabilities
    """

    def __init__(self):
        """Initialize the guide generator with required services."""
        self.glean_client = GleanClient()
        self.prompt_builder = PromptBuilder()

    async def generate_guide(
        self,
        transcript: str,
        company_name: str,
        additional_context: str | None = None,
    ) -> str:
        """Generate a complete solution guide from a call transcript.

        Args:
            transcript: The call transcript content
            company_name: Name of the target company
            additional_context: Optional additional context about the use case

        Returns:
            Generated solution guide in markdown format

        Raises:
            Exception: If the guide generation process fails
        """
        try:
            logger.info(f"Starting guide generation for {company_name}")

            # Step 1: Research the company using Glean
            logger.info(f"Researching company: {company_name}")
            company_insights = await self._research_company(company_name, transcript, additional_context)

            # Step 2: Build the prompt for guide generation
            logger.info("Building solution guide prompt")
            prompt = self.prompt_builder.build_solution_guide_prompt(
                transcript=transcript,
                company_name=company_name,
                company_research=company_insights,
                additional_context=additional_context,
            )

            # Step 3: Generate the guide using Glean chat
            logger.info("Generating solution guide")
            solution_guide = await self.glean_client.chat_query(prompt)

            # Step 4: Post-process and validate the guide
            processed_guide = self._post_process_guide(solution_guide, company_name)

            logger.info(f"Successfully generated guide for {company_name}")
            return processed_guide

        except Exception as e:
            logger.error(f"Error generating guide for {company_name}: {e}")
            raise Exception(f"Failed to generate solution guide: {str(e)}")

    async def _research_company(
        self,
        company_name: str,
        transcript: str,
        additional_context: str | None = None,
    ) -> dict[str, Any]:
        """Research the company to gather relevant business and technical context.

        Args:
            company_name: Name of the company to research
            transcript: Call transcript for context
            additional_context: Optional additional context

        Returns:
            Dictionary containing company research results
        """
        try:
            # Extract use case from transcript and additional context
            use_case = self._extract_use_case(transcript, additional_context)

            # Get comprehensive company insights
            insights = await self.glean_client.get_company_insights(company_name, use_case)

            # Enhance insights with transcript-specific research
            if len(transcript) > 500:  # Only if transcript is substantial
                transcript_excerpt = transcript[:1000] + "..." if len(transcript) > 1000 else transcript
                research_prompt = self.prompt_builder.build_company_research_prompt(company_name, transcript_excerpt)
                additional_research = await self.glean_client.chat_query(research_prompt)
                insights["transcript_analysis"] = additional_research

            return insights

        except Exception as e:
            logger.error(f"Error researching company {company_name}: {e}")
            return {
                "company_name": company_name,
                "business_overview": f"Unable to research {company_name}. Error: {str(e)}",
                "technical_context": "No technical context available due to research error.",
                "error": str(e),
            }

    def _extract_use_case(self, transcript: str, additional_context: str | None = None) -> str:
        """Extract the primary use case from transcript and context.

        Args:
            transcript: Call transcript content
            additional_context: Optional additional context

        Returns:
            Extracted use case description
        """
        use_case_parts = []

        # Add additional context if provided
        if additional_context:
            use_case_parts.append(additional_context)

        # Extract key phrases from transcript that indicate use cases
        use_case_keywords = [
            "payment",
            "transaction",
            "bank",
            "financial",
            "integration",
            "API",
            "platform",
            "system",
            "application",
            "service",
        ]

        # Look for sentences containing use case keywords
        sentences = transcript.split(".")
        relevant_sentences = []

        for sentence in sentences[:20]:  # Only check first 20 sentences
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in use_case_keywords):
                relevant_sentences.append(sentence.strip())

        if relevant_sentences:
            use_case_parts.extend(relevant_sentences[:3])  # Top 3 relevant sentences

        return " ".join(use_case_parts) if use_case_parts else "financial technology integration"

    def _post_process_guide(self, raw_guide: str, company_name: str) -> str:
        """Post-process the generated guide to ensure quality and formatting.

        Args:
            raw_guide: The raw generated guide content
            company_name: Company name for validation

        Returns:
            Post-processed and validated guide
        """
        try:
            # Basic validation - ensure guide contains expected sections
            required_sections = [
                "Solutions Guide",
                "What You're Building",
                "Integration",
                "Technical",
                "Getting Started",
            ]

            guide_content = raw_guide

            # Check if guide has proper structure
            missing_sections = [
                section for section in required_sections if section.lower() not in guide_content.lower()
            ]

            if missing_sections:
                logger.warning(f"Generated guide missing sections: {missing_sections}")

            # Ensure proper title format
            if not guide_content.startswith(f"# {company_name}"):
                lines = guide_content.split("\n")
                has_h1_title = any(line.startswith("# ") for line in lines)

                if has_h1_title:
                    # Fix existing h1 title
                    for i, line in enumerate(lines):
                        if line.startswith("# "):
                            lines[i] = f"# {company_name} + Plaid // Solutions Guide"
                            break
                    guide_content = "\n".join(lines)
                else:
                    # Add title if missing
                    guide_content = f"# {company_name} + Plaid // Solutions Guide\n\n{guide_content}"

            # Clean up any formatting issues
            guide_content = guide_content.replace("\n\n\n", "\n\n")  # Remove excessive newlines
            guide_content = guide_content.strip()  # Remove leading/trailing whitespace

            return guide_content

        except Exception as e:
            logger.error(f"Error post-processing guide: {e}")
            # Return raw guide if post-processing fails
            return raw_guide

    async def validate_environment(self) -> dict[str, bool]:
        """Validate that the environment is properly configured.

        Returns:
            Dictionary with validation results for different components
        """
        validation_results = {
            "glean_client": False,
            "configuration": False,
            "connectivity": False,
        }

        try:
            # Test configuration
            from app.config import get_settings

            settings = get_settings()

            if settings.glean_instance and settings.glean_api_token:
                validation_results["configuration"] = True

            # Test Glean connectivity
            test_response = await self.glean_client.chat_query("Hello, this is a test.")
            if "error" not in test_response.lower():
                validation_results["glean_client"] = True
                validation_results["connectivity"] = True

        except Exception as e:
            logger.error(f"Environment validation failed: {e}")

        return validation_results
