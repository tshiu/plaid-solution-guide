"""Glean API client for company research and insights."""

import logging
from typing import Any

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


class GleanClient:
    """Client for interacting with Glean APIs.

    This client handles all interactions with Glean's search and chat APIs
    to gather company information and insights for solution guide generation.
    """

    def __init__(self):
        """Initialize Glean client with configuration from environment."""
        settings = get_settings()
        self.base_url = f"https://{settings.glean_instance}"
        self.headers = {
            "Authorization": f"Bearer {settings.glean_api_token}",
            "Content-Type": "application/json",
        }
        self.timeout = 30.0

    async def search_company(self, company_name: str) -> dict[str, Any]:
        """Search for company information using Glean's search API.

        Args:
            company_name: Name of the company to search for

        Returns:
            Dictionary containing search results and company information

        Raises:
            httpx.HTTPError: If the API request fails
        """
        try:
            search_query = f"company information about {company_name} business model products services"

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/search",
                    headers=self.headers,
                    json={
                        "query": search_query,
                        "datasources": ["drive", "confluence", "github"],
                        "pageSize": 5,
                    },
                )
                response.raise_for_status()

                result = response.json()
                logger.info(f"Successfully searched for company: {company_name}")
                return result

        except httpx.HTTPError as e:
            logger.error(f"Error searching for company {company_name}: {e}")
            return {"results": [], "error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error searching for company {company_name}: {e}")
            return {"results": [], "error": str(e)}

    async def chat_query(self, message: str, context: list[str] | None = None) -> str:
        """Query Glean chat for additional insights and information.

        Args:
            message: The question or query to ask Glean
            context: Optional list of previous messages for context

        Returns:
            String response from Glean chat

        Raises:
            httpx.HTTPError: If the API request fails
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {"message": message}

                if context:
                    payload["context"] = context

                response = await client.post(f"{self.base_url}/api/chat", headers=self.headers, json=payload)
                response.raise_for_status()

                result = response.json()
                logger.info("Successfully queried Glean chat")

                # Extract the response text from the result
                if isinstance(result, dict) and "response" in result:
                    return result["response"]
                elif isinstance(result, dict) and "message" in result:
                    return result["message"]
                else:
                    return str(result)

        except httpx.HTTPError as e:
            logger.error(f"Error querying Glean chat: {e}")
            return f"Error querying Glean: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error querying Glean chat: {e}")
            return f"Unexpected error: {str(e)}"

    async def get_company_insights(self, company_name: str, use_case: str | None = None) -> dict[str, Any]:
        """Get comprehensive company insights combining search and chat.

        Args:
            company_name: Name of the company to research
            use_case: Optional use case context to focus the research

        Returns:
            Dictionary containing comprehensive company insights
        """
        insights = {
            "company_name": company_name,
            "search_results": {},
            "business_overview": "",
            "technical_context": "",
            "relevant_info": [],
        }

        try:
            # First, search for company information
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
            insights["error"] = str(e)
            return insights
