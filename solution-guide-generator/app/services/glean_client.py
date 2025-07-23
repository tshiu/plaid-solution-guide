"""Glean API client for company research and insights using official SDK."""

import logging
from typing import Any

from glean.api_client import Glean, models

from app.config import get_settings

logger = logging.getLogger(__name__)


class GleanClient:
    """Client for interacting with Glean APIs using the official SDK.

    This client provides a convenient interface for company research and
    chat functionality using Glean's official Python SDK.
    """

    def __init__(self):
        """Initialize Glean client with configuration from environment."""
        settings = get_settings()
        self.settings = settings
        self._client = None

    def _get_client(self) -> Glean:
        """Get or create the Glean client instance."""
        if self._client is None:
            # Use instance name as provided - SDK handles URL construction
            self._client = Glean(
                api_token=self.settings.glean_api_token,
                instance=self.settings.glean_instance.strip(),
            )
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
        try:
            search_query = f"company information about {company_name} business model products services"

            client = self._get_client()

            # Use the official SDK's search API
            search_response = await client.client.search.query_async(
                query=search_query,
                page_size=10,
                request_options=models.SearchRequestOptions(
                    # Focus on high-level company information
                    facet_filters=[],
                    facet_bucket_size=10,
                ),
            )

            # Extract relevant information from search results
            results = []
            if hasattr(search_response, "results") and search_response.results:
                for result in search_response.results[:5]:  # Top 5 results
                    result_info = {
                        "title": getattr(result, "title", ""),
                        "snippet": getattr(result, "snippet", ""),
                        "url": getattr(result, "url", ""),
                    }
                    results.append(result_info)

            return {
                "results": results,
                "query": search_query,
                "total_results": len(results),
            }

        except Exception as e:
            logger.error(f"Error searching for company {company_name}: {e}")
            return {
                "error": f"Search failed: {str(e)}",
                "results": [],
                "query": search_query,
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
        try:
            client = self._get_client()

            # Build messages for the chat
            messages = []

            # Add context messages if provided
            if context:
                for ctx in context:
                    messages.append({"fragments": [models.ChatMessageFragment(text=ctx)]})

            # Add the main question
            messages.append({"fragments": [models.ChatMessageFragment(text=question)]})

            # Use the official SDK's chat API
            chat_response = await client.client.chat.create_async(
                messages=messages,
                timeout_millis=30_000,
            )

            # Extract the response text
            if hasattr(chat_response, "messages") and chat_response.messages:
                # Get the last message (AI response)
                last_message = chat_response.messages[-1]
                if hasattr(last_message, "fragments") and last_message.fragments:
                    # Combine all fragments into a single response
                    response_parts = []
                    for fragment in last_message.fragments:
                        if hasattr(fragment, "text"):
                            response_parts.append(fragment.text)
                    return " ".join(response_parts)

            # Fallback for different response structures
            if hasattr(chat_response, "text"):
                return chat_response.text
            elif hasattr(chat_response, "content"):
                return chat_response.content
            else:
                logger.warning(f"Unexpected chat response structure: {type(chat_response)}")
                return str(chat_response)

        except Exception as e:
            logger.error(f"Error in chat query '{question}': {e}")
            return f"Chat query failed: {str(e)}"

    async def get_company_insights(self, company_name: str, use_case: str | None = None) -> dict[str, Any]:
        """Get comprehensive company insights using both search and chat.

        Args:
            company_name: Name of the company to research
            use_case: Optional specific use case to focus research on

        Returns:
            Dictionary containing comprehensive company insights
        """
        insights = {"company_name": company_name}

        try:
            # First, search for basic company information
            search_results = await self.search_company(company_name)
            insights["search_results"] = search_results

            # Then, ask Glean chat for business overview
            business_query = (
                f"Tell me about {company_name} - what is their business model, "
                f"what products/services do they offer, and what industry are they in?"
            )
            if use_case:
                business_query += f" Focus on aspects relevant to {use_case}."

            business_overview = await self.chat_query(business_query)
            insights["business_overview"] = business_overview

            # Get technical context if use case provided
            if use_case:
                tech_query = (
                    f"What technical challenges might {company_name} face when implementing {use_case}? "
                    f"What integration considerations should we be aware of?"
                )
                technical_context = await self.chat_query(tech_query)
                insights["technical_context"] = technical_context

            return insights

        except Exception as e:
            logger.error(f"Error getting company insights for {company_name}: {e}")
            return {
                "company_name": company_name,
                "error": f"Unable to research {company_name}: {str(e)}",
                "business_overview": "",
                "technical_context": "",
                "search_results": {"results": [], "total_results": 0},
            }

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup client if needed."""
        if self._client:
            # The official SDK should handle cleanup automatically
            pass
