"""Glean API client for company research and insights using official SDK."""

import logging
import time
from typing import Any

from glean.api_client import Glean, errors

from app.config import get_settings

logger = logging.getLogger(__name__)


class GleanClient:
    """Client for interacting with Glean APIs using the official SDK.

    This client provides a convenient interface for company research and
    chat functionality using Glean's official Python SDK.
    """

    def __init__(self):
        """Initialize Glean client with configuration from environment."""
        logger.info("🔧 Initializing Glean client...")
        settings = get_settings()
        self.settings = settings
        self._client = None
        logger.info(f"✅ Glean client configured for instance: {settings.glean_instance}")

    def _get_client(self) -> Glean:
        """Get or create the Glean client instance."""
        if self._client is None:
            logger.info("🔌 Creating new Glean API client connection...")
            self._client = Glean(
                api_token=self.settings.glean_api_token,
                instance=self.settings.glean_instance,
            )
            logger.info("✅ Glean API client connected successfully")
        return self._client

    async def search_company(self, company_name: str) -> dict[str, Any]:
        """Search for company information using Glean's search API.

        Args:
            company_name: Name of the company to search for

        Returns:
            Dictionary containing search results and company information

        Raises:
            Exception: If the API request fails
        """
        logger.info(f"🔍 Starting company search for: '{company_name}'")
        start_time = time.time()

        try:
            search_query = f"company information about {company_name} business model products services"
            logger.info(f"   Search query: '{search_query}'")

            client = self._get_client()
            logger.info("   Making API call to Glean search endpoint...")

            # Use the official SDK's search API
            search_response = client.client.search.query(query=search_query, page_size=10)

            api_time = time.time() - start_time
            logger.info(f"   ✅ Glean search API responded in {api_time:.2f}s")

            # Extract relevant information from search results
            results = []
            if hasattr(search_response, "results") and search_response.results:
                logger.info(f"   Found {len(search_response.results)} search results")
                for i, result in enumerate(search_response.results[:5], 1):  # Top 5 results
                    result_info = {
                        "title": getattr(result, "title", ""),
                        "snippet": getattr(result, "snippet", ""),
                        "url": getattr(result, "url", ""),
                    }
                    results.append(result_info)
                    logger.info(f"   📄 Result {i}: {result_info['title'][:50]}...")
            else:
                logger.warning("   No search results found in response")

            total_time = time.time() - start_time
            final_results = {
                "results": results,
                "query": search_query,
                "total_results": len(results),
            }

            logger.info(f"🎉 Company search completed for '{company_name}' in {total_time:.2f}s")
            logger.info(f"   Returning {len(results)} results")
            return final_results

        except errors.GleanError as e:
            error_time = time.time() - start_time
            logger.error(f"❌ Glean API error searching for company '{company_name}' after {error_time:.2f}s:")
            logger.error(f"   Error type: {type(e).__name__}")
            logger.error(f"   Error message: {str(e)}")
            return {
                "error": f"Search failed: {str(e)}",
                "results": [],
                "query": search_query,
                "total_results": 0,
            }
        except Exception as e:
            error_time = time.time() - start_time
            logger.error(f"💥 Unexpected error searching for company '{company_name}' after {error_time:.2f}s:")
            logger.error(f"   Error type: {type(e).__name__}")
            logger.error(f"   Error message: {str(e)}")
            return {
                "error": f"Search failed: {str(e)}",
                "results": [],
                "query": search_query if "search_query" in locals() else "",
                "total_results": 0,
            }

    async def chat_query(self, question: str, context: list[str] | None = None) -> str:
        """Send a chat query to Glean's AI chat API.

        Args:
            question: The question to ask
            context: Optional list of context messages

        Returns:
            The AI's response as a string

        Raises:
            Exception: If the API request fails
        """
        logger.info("💬 Starting Glean chat query...")
        logger.info(f"   Question length: {len(question)} characters")
        logger.info(f"   Question preview: {question[:100]}...")
        if context:
            logger.info(f"   Including {len(context)} context messages")

        start_time = time.time()

        try:
            client = self._get_client()

            # Build messages for the chat
            messages = []

            # Add context messages if provided
            if context:
                logger.info("   Adding context messages to chat...")
                for i, ctx in enumerate(context, 1):
                    messages.append({"fragments": [{"text": ctx}]})
                    logger.info(f"     Context {i}: {ctx[:50]}...")

            # Add the main question
            messages.append({"fragments": [{"text": question}]})
            logger.info(f"   Built chat with {len(messages)} total messages")

            logger.info("   Making API call to Glean chat endpoint...")
            # Use the official SDK's chat API
            chat_response = client.client.chat.create(messages=messages, timeout_millis=30_000)

            api_time = time.time() - start_time
            logger.info(f"   ✅ Glean chat API responded in {api_time:.2f}s")

            # Extract the response text from the last message
            response_text = ""
            if hasattr(chat_response, "messages") and chat_response.messages:
                logger.info(f"   Chat response contains {len(chat_response.messages)} messages")
                # Get the last message (AI response)
                last_message = chat_response.messages[-1]
                if hasattr(last_message, "fragments") and last_message.fragments:
                    # Combine all fragments into a single response
                    response_parts = []
                    for fragment in last_message.fragments:
                        if hasattr(fragment, "text") and fragment.text:
                            response_parts.append(fragment.text)
                    response_text = " ".join(response_parts)
                    logger.info(f"   Combined {len(response_parts)} text fragments")
            elif hasattr(chat_response, "text") and chat_response.text:
                response_text = chat_response.text
                logger.info("   Using direct text response")
            elif hasattr(chat_response, "content"):
                response_text = chat_response.content
                logger.info("   Using content field as response")
            else:
                logger.warning(f"   Unexpected chat response structure: {type(chat_response)}")
                response_text = str(chat_response)

            total_time = time.time() - start_time
            logger.info(f"🎉 Chat query completed in {total_time:.2f}s")
            logger.info(f"   Response length: {len(response_text)} characters")
            logger.info(f"   Response preview: {response_text[:100]}...")

            return response_text

        except errors.GleanError as e:
            error_time = time.time() - start_time
            logger.error(f"❌ Glean API error in chat query after {error_time:.2f}s:")
            logger.error(f"   Error type: {type(e).__name__}")
            logger.error(f"   Error message: {str(e)}")
            logger.error(f"   Question was: {question[:100]}...")
            return f"Chat query failed: {str(e)}"
        except Exception as e:
            error_time = time.time() - start_time
            logger.error(f"💥 Unexpected error in chat query after {error_time:.2f}s:")
            logger.error(f"   Error type: {type(e).__name__}")
            logger.error(f"   Error message: {str(e)}")
            logger.error(f"   Question was: {question[:100]}...")
            return f"Chat query failed: {str(e)}"

    async def get_company_insights(self, company_name: str, use_case: str | None = None) -> dict[str, Any]:
        """Get comprehensive company insights using both search and chat.

        Args:
            company_name: Name of the company to research
            use_case: Optional specific use case to focus research on

        Returns:
            Dictionary containing comprehensive company insights
        """
        logger.info(f"🔬 Starting comprehensive company insights for: '{company_name}'")
        if use_case:
            logger.info(f"   Focusing on use case: '{use_case}'")

        insights = {"company_name": company_name}
        overall_start = time.time()

        try:
            # First, search for basic company information
            logger.info("📋 Step 1: Searching for basic company information...")
            search_results = await self.search_company(company_name)
            insights["search_results"] = search_results

            if "error" in search_results:
                logger.warning(f"   Search step had errors: {search_results['error']}")
            else:
                logger.info(f"   Search step completed successfully with {search_results['total_results']} results")

            # Then, ask Glean chat for business overview
            logger.info("💼 Step 2: Getting business overview from chat...")
            business_query = (
                f"Tell me about {company_name} - what is their business model, "
                f"what products/services do they offer, and what industry are they in?"
            )
            if use_case:
                business_query += f" Focus on aspects relevant to {use_case}."
                logger.info("   Enhanced query with use case context")

            business_overview = await self.chat_query(business_query)
            insights["business_overview"] = business_overview

            if "failed" in business_overview.lower():
                logger.warning("   Business overview query had issues")
            else:
                logger.info("   Business overview obtained successfully")

            # Get technical context if use case provided
            if use_case:
                logger.info("⚙️  Step 3: Getting technical context for use case...")
                tech_query = (
                    f"What technical challenges might {company_name} face when implementing {use_case}? "
                    f"What integration considerations should we be aware of?"
                )
                technical_context = await self.chat_query(tech_query)
                insights["technical_context"] = technical_context

                if "failed" in technical_context.lower():
                    logger.warning("   Technical context query had issues")
                else:
                    logger.info("   Technical context obtained successfully")
            else:
                logger.info("   Skipping technical context (no use case provided)")

            total_time = time.time() - overall_start
            logger.info(f"🎉 Company insights completed for '{company_name}' in {total_time:.2f}s")

            return insights

        except Exception as e:
            error_time = time.time() - overall_start
            logger.error(f"💥 Error getting company insights for '{company_name}' after {error_time:.2f}s:")
            logger.error(f"   Error type: {type(e).__name__}")
            logger.error(f"   Error message: {str(e)}")

            return {
                "company_name": company_name,
                "error": f"Unable to research {company_name}: {str(e)}",
                "business_overview": "",
                "technical_context": "",
                "search_results": {"results": [], "total_results": 0},
            }

    def __enter__(self):
        """Context manager entry."""
        logger.info("🔧 Entering Glean client context")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup client if needed."""
        logger.info("🔧 Exiting Glean client context")
        if self._client:
            # The official SDK should handle cleanup automatically
            pass
