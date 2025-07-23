"""Main service for generating solution guides from transcripts."""

import logging
import time
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
        logger.info("🏗️  Initializing Guide Generator...")
        self.glean_client = GleanClient()
        self.prompt_builder = PromptBuilder()
        logger.info("✅ Guide Generator initialized with Glean client and prompt builder")

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
        logger.info("=" * 60)
        logger.info("🚀 STARTING GUIDE GENERATION")
        logger.info(f"   Company: {company_name}")
        logger.info(f"   Transcript length: {len(transcript)} characters")
        logger.info(f"   Has additional context: {bool(additional_context)}")
        logger.info("=" * 60)

        overall_start = time.time()

        try:
            # Step 1: Research the company using Glean
            logger.info(f"📊 STEP 1: Researching company '{company_name}'")
            step1_start = time.time()

            company_insights = await self._research_company(company_name, transcript, additional_context)

            step1_time = time.time() - step1_start
            logger.info(f"✅ STEP 1 COMPLETE: Company research finished in {step1_time:.2f}s")

            if "error" in company_insights:
                logger.warning(f"   ⚠️  Research had issues: {company_insights['error']}")
            else:
                logger.info("   Research appears successful")

            # Step 2: Build the prompt for guide generation
            logger.info("📝 STEP 2: Building solution guide prompt")
            step2_start = time.time()

            prompt = self.prompt_builder.build_solution_guide_prompt(
                transcript=transcript,
                company_name=company_name,
                company_research=company_insights,
                additional_context=additional_context,
            )

            step2_time = time.time() - step2_start
            logger.info(f"✅ STEP 2 COMPLETE: Prompt built in {step2_time:.3f}s")
            logger.info(f"   Prompt length: {len(prompt)} characters")

            # Step 3: Generate the guide using Glean chat
            logger.info("🤖 STEP 3: Generating solution guide with AI")
            step3_start = time.time()

            solution_guide = await self.glean_client.chat_query(prompt)

            step3_time = time.time() - step3_start
            logger.info(f"✅ STEP 3 COMPLETE: AI generation finished in {step3_time:.2f}s")
            logger.info(f"   Generated guide length: {len(solution_guide)} characters")

            # Step 4: Post-process and validate the guide
            logger.info("✨ STEP 4: Post-processing and validating guide")
            step4_start = time.time()

            processed_guide = self._post_process_guide(solution_guide, company_name)

            step4_time = time.time() - step4_start
            logger.info(f"✅ STEP 4 COMPLETE: Post-processing finished in {step4_time:.3f}s")
            logger.info(f"   Final guide length: {len(processed_guide)} characters")

            total_time = time.time() - overall_start
            logger.info("=" * 60)
            logger.info("🎉 GUIDE GENERATION SUCCESSFUL!")
            logger.info(f"   Total time: {total_time:.2f}s")
            logger.info(f"   Company: {company_name}")
            logger.info(f"   Final guide: {len(processed_guide)} characters")
            logger.info("=" * 60)

            return processed_guide

        except Exception as e:
            error_time = time.time() - overall_start
            logger.error("=" * 60)
            logger.error("💥 GUIDE GENERATION FAILED!")
            logger.error(f"   Company: {company_name}")
            logger.error(f"   Time before failure: {error_time:.2f}s")
            logger.error(f"   Error type: {type(e).__name__}")
            logger.error(f"   Error message: {str(e)}")
            logger.error("=" * 60)
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
        logger.info(f"🔍 Starting detailed company research for '{company_name}'")
        research_start = time.time()

        try:
            # Extract use case from transcript and additional context
            logger.info("📋 Extracting use case from transcript and context...")
            use_case = self._extract_use_case(transcript, additional_context)
            logger.info(f"   Extracted use case: '{use_case}'")

            # Get comprehensive company insights
            logger.info("🔬 Getting comprehensive company insights...")
            insights = await self.glean_client.get_company_insights(company_name, use_case)

            # Enhance insights with transcript-specific research
            if len(transcript) > 500:  # Only if transcript is substantial
                logger.info("📄 Transcript is substantial - doing additional analysis...")
                logger.info(f"   Transcript length: {len(transcript)} characters")

                transcript_excerpt = transcript[:1000] + "..." if len(transcript) > 1000 else transcript
                logger.info(f"   Using excerpt of {len(transcript_excerpt)} characters")

                research_prompt = self.prompt_builder.build_company_research_prompt(company_name, transcript_excerpt)
                logger.info("   Built research prompt, querying AI...")

                additional_research = await self.glean_client.chat_query(research_prompt)
                insights["transcript_analysis"] = additional_research
                logger.info(f"   Additional research completed: {len(additional_research)} characters")
            else:
                logger.info("📄 Transcript too short - skipping additional analysis")
                logger.info(f"   Transcript length: {len(transcript)} characters (minimum: 500)")

            research_time = time.time() - research_start
            logger.info(f"✅ Company research completed in {research_time:.2f}s")

            return insights

        except Exception as e:
            error_time = time.time() - research_start
            logger.error(f"❌ Error researching company '{company_name}' after {error_time:.2f}s:")
            logger.error(f"   Error type: {type(e).__name__}")
            logger.error(f"   Error message: {str(e)}")

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
        logger.info("🎯 Extracting use case from provided content...")

        use_case_parts = []

        # Add additional context if provided
        if additional_context:
            use_case_parts.append(additional_context)
            logger.info(f"   Added additional context: {additional_context[:100]}...")

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
        logger.info(f"   Looking for use case keywords: {use_case_keywords}")

        # Look for sentences containing use case keywords
        sentences = transcript.split(".")
        relevant_sentences = []

        logger.info(f"   Analyzing {len(sentences)} sentences from transcript...")
        for sentence in sentences[:20]:  # Only check first 20 sentences
            sentence_lower = sentence.lower()
            matching_keywords = [kw for kw in use_case_keywords if kw in sentence_lower]
            if matching_keywords:
                relevant_sentences.append(sentence.strip())
                logger.info(f"     Found relevant sentence with {matching_keywords}: {sentence[:50]}...")

        if relevant_sentences:
            use_case_parts.extend(relevant_sentences[:3])  # Top 3 relevant sentences
            logger.info(f"   Selected {len(relevant_sentences[:3])} relevant sentences")
        else:
            logger.info("   No relevant sentences found, using default")

        final_use_case = " ".join(use_case_parts) if use_case_parts else "financial technology integration"
        logger.info(f"   Final extracted use case: '{final_use_case[:100]}...'")

        return final_use_case

    def _post_process_guide(self, raw_guide: str, company_name: str) -> str:
        """Post-process the generated guide to ensure quality and formatting.

        Args:
            raw_guide: The raw generated guide content
            company_name: Company name for validation

        Returns:
            Post-processed and validated guide
        """
        logger.info("✨ Starting guide post-processing...")
        logger.info(f"   Raw guide length: {len(raw_guide)} characters")

        try:
            # Basic validation - ensure guide contains expected sections
            required_sections = [
                "Solutions Guide",
                "What You're Building",
                "Integration",
                "Technical",
                "Getting Started",
            ]
            logger.info(f"   Checking for required sections: {required_sections}")

            guide_content = raw_guide

            # Check if guide has proper structure
            missing_sections = [
                section for section in required_sections if section.lower() not in guide_content.lower()
            ]

            if missing_sections:
                logger.warning(f"   ⚠️  Generated guide missing sections: {missing_sections}")
            else:
                logger.info("   ✅ All required sections found")

            # Ensure proper title format
            logger.info("   Checking and fixing title format...")
            if not guide_content.startswith(f"# {company_name}"):
                lines = guide_content.split("\n")
                has_h1_title = any(line.startswith("# ") for line in lines)

                if has_h1_title:
                    # Fix existing h1 title
                    for i, line in enumerate(lines):
                        if line.startswith("# "):
                            old_title = line
                            lines[i] = f"# {company_name} + Plaid // Solutions Guide"
                            logger.info(f"     Fixed title: '{old_title}' → '{lines[i]}'")
                            break
                    guide_content = "\n".join(lines)
                else:
                    # Add title if missing
                    new_title = f"# {company_name} + Plaid // Solutions Guide"
                    guide_content = f"{new_title}\n\n{guide_content}"
                    logger.info(f"     Added missing title: '{new_title}'")
            else:
                logger.info("   Title format already correct")

            # Clean up any formatting issues
            logger.info("   Cleaning up formatting...")
            old_length = len(guide_content)
            guide_content = guide_content.replace("\n\n\n", "\n\n")  # Remove excessive newlines
            guide_content = guide_content.strip()  # Remove leading/trailing whitespace
            new_length = len(guide_content)

            if old_length != new_length:
                logger.info(f"   Cleaned up formatting: {old_length} → {new_length} characters")

            logger.info(f"✅ Post-processing complete: {len(guide_content)} characters")
            return guide_content

        except Exception as e:
            logger.error(f"❌ Error post-processing guide: {type(e).__name__}: {str(e)}")
            logger.warning("   Returning raw guide due to post-processing failure")
            return raw_guide

    async def validate_environment(self) -> dict[str, bool]:
        """Validate that the environment is properly configured.

        Returns:
            Dictionary with validation results for different components
        """
        logger.info("🔧 Starting environment validation...")

        validation_results = {
            "glean_client": False,
            "configuration": False,
            "connectivity": False,
        }

        try:
            # Test configuration
            logger.info("   Testing configuration...")
            from app.config import get_settings

            settings = get_settings()

            if settings.glean_instance and settings.glean_api_token:
                validation_results["configuration"] = True
                logger.info("   ✅ Configuration valid")
                logger.info(f"     Instance: {settings.glean_instance}")
                logger.info(f"     Token: {'*' * 20}...")
            else:
                logger.error("   ❌ Configuration invalid")
                logger.error(f"     Instance: {settings.glean_instance or 'NOT SET'}")
                logger.error(f"     Token: {'SET' if settings.glean_api_token else 'NOT SET'}")

            # Test Glean connectivity
            logger.info("   Testing Glean connectivity...")
            test_response = await self.glean_client.chat_query("Hello, this is a test.")

            if "error" not in test_response.lower() and "failed" not in test_response.lower():
                validation_results["glean_client"] = True
                validation_results["connectivity"] = True
                logger.info("   ✅ Glean connectivity successful")
                logger.info(f"     Test response: {test_response[:50]}...")
            else:
                logger.error("   ❌ Glean connectivity failed")
                logger.error(f"     Test response: {test_response[:100]}...")

        except Exception as e:
            logger.error(f"❌ Environment validation failed: {type(e).__name__}: {str(e)}")

        logger.info(f"🔧 Environment validation complete: {validation_results}")
        return validation_results
