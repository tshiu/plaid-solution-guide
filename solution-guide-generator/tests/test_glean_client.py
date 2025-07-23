"""Tests for GleanClient using official SDK."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.glean_client import GleanClient


class TestGleanClient:
    """Test cases for GleanClient with official SDK."""

    @pytest.fixture
    def glean_client(self):
        """Create a GleanClient instance for testing."""
        with patch("app.services.glean_client.get_settings") as mock_get_settings:
            mock_settings = MagicMock()
            mock_settings.glean_instance = "test-instance"
            mock_settings.glean_api_token = "test-token"
            mock_get_settings.return_value = mock_settings
            return GleanClient()

    @pytest.mark.asyncio
    async def test_search_company_success(self, glean_client):
        """Test successful company search."""
        # Mock the official SDK's search response
        mock_search_result = MagicMock()
        mock_search_result.title = "Test Company"
        mock_search_result.snippet = "Test company description"
        mock_search_result.url = "https://example.com"

        mock_search_response = MagicMock()
        mock_search_response.results = [mock_search_result]

        # Mock the Glean SDK client
        with patch.object(glean_client, "_get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.client.search.query_async = AsyncMock(return_value=mock_search_response)
            mock_get_client.return_value = mock_client

            result = await glean_client.search_company("TestCorp")

            assert result["total_results"] == 1
            assert len(result["results"]) == 1
            assert result["results"][0]["title"] == "Test Company"
            assert result["results"][0]["snippet"] == "Test company description"
            assert result["query"] == "company information about TestCorp business model products services"

    @pytest.mark.asyncio
    async def test_search_company_http_error(self, glean_client):
        """Test company search with API error."""
        # Mock the Glean SDK to raise an exception
        with patch.object(glean_client, "_get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.client.search.query_async = AsyncMock(side_effect=Exception("API Error"))
            mock_get_client.return_value = mock_client

            result = await glean_client.search_company("TestCorp")

            assert "error" in result
            assert "Search failed" in result["error"]
            assert result["total_results"] == 0

    @pytest.mark.asyncio
    async def test_chat_query_success(self, glean_client):
        """Test successful chat query."""
        # Mock the official SDK's chat response
        mock_fragment = MagicMock()
        mock_fragment.text = "Test chat response"

        mock_message = MagicMock()
        mock_message.fragments = [mock_fragment]

        mock_chat_response = MagicMock()
        mock_chat_response.messages = [mock_message]

        # Mock the Glean SDK client
        with patch.object(glean_client, "_get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.client.chat.create_async = AsyncMock(return_value=mock_chat_response)
            mock_get_client.return_value = mock_client

            result = await glean_client.chat_query("Test question")

            assert result == "Test chat response"

    @pytest.mark.asyncio
    async def test_chat_query_with_context(self, glean_client):
        """Test chat query with context."""
        # Mock the official SDK's chat response
        mock_fragment = MagicMock()
        mock_fragment.text = "Contextual response"

        mock_message = MagicMock()
        mock_message.fragments = [mock_fragment]

        mock_chat_response = MagicMock()
        mock_chat_response.messages = [mock_message]

        context = ["Previous message 1", "Previous message 2"]

        # Mock the Glean SDK client
        with patch.object(glean_client, "_get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.client.chat.create_async = AsyncMock(return_value=mock_chat_response)
            mock_get_client.return_value = mock_client

            result = await glean_client.chat_query("Test question", context)

            assert result == "Contextual response"
            # Verify that context messages were included
            call_args = mock_client.client.chat.create_async.call_args
            messages = call_args.kwargs["messages"]
            assert len(messages) == 3  # 2 context + 1 question

    @pytest.mark.asyncio
    async def test_chat_query_http_error(self, glean_client):
        """Test chat query with API error."""
        # Mock the Glean SDK to raise an exception
        with patch.object(glean_client, "_get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.client.chat.create_async = AsyncMock(side_effect=Exception("Chat API Error"))
            mock_get_client.return_value = mock_client

            result = await glean_client.chat_query("Test question")

            assert "Chat query failed" in result

    @pytest.mark.asyncio
    async def test_get_company_insights_success(self, glean_client):
        """Test successful company insights gathering."""
        # Mock search results
        mock_search_result = MagicMock()
        mock_search_result.title = "Company Info"
        mock_search_result.snippet = "Company description"
        mock_search_result.url = "https://example.com"

        mock_search_response = MagicMock()
        mock_search_response.results = [mock_search_result]

        # Mock chat response
        mock_fragment = MagicMock()
        mock_fragment.text = "Business overview response"

        mock_message = MagicMock()
        mock_message.fragments = [mock_fragment]

        mock_chat_response = MagicMock()
        mock_chat_response.messages = [mock_message]

        # Mock the Glean SDK client
        with patch.object(glean_client, "_get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.client.search.query_async = AsyncMock(return_value=mock_search_response)
            mock_client.client.chat.create_async = AsyncMock(return_value=mock_chat_response)
            mock_get_client.return_value = mock_client

            result = await glean_client.get_company_insights("TestCorp")

            assert result["company_name"] == "TestCorp"
            assert "search_results" in result
            assert "business_overview" in result
            assert result["business_overview"] == "Business overview response"

    @pytest.mark.asyncio
    async def test_get_company_insights_with_use_case(self, glean_client):
        """Test company insights with specific use case."""
        # Mock search results
        mock_search_response = MagicMock()
        mock_search_response.results = []

        # Mock chat responses (business + technical)
        mock_fragment = MagicMock()
        mock_fragment.text = "Use case specific response"

        mock_message = MagicMock()
        mock_message.fragments = [mock_fragment]

        mock_chat_response = MagicMock()
        mock_chat_response.messages = [mock_message]

        # Mock the Glean SDK client
        with patch.object(glean_client, "_get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.client.search.query_async = AsyncMock(return_value=mock_search_response)
            mock_client.client.chat.create_async = AsyncMock(return_value=mock_chat_response)
            mock_get_client.return_value = mock_client

            result = await glean_client.get_company_insights("TestCorp", "payment processing")

            assert result["company_name"] == "TestCorp"
            assert "technical_context" in result
            assert result["technical_context"] == "Use case specific response"

    @pytest.mark.asyncio
    async def test_get_company_insights_error_handling(self, glean_client):
        """Test company insights error handling."""
        # Mock the Glean SDK to raise an exception from _get_client itself
        with patch.object(glean_client, "_get_client") as mock_get_client:
            mock_get_client.side_effect = Exception("Failed to initialize client")

            result = await glean_client.get_company_insights("TestCorp")

            # The method gracefully handles errors by setting error messages in components
            assert result["company_name"] == "TestCorp"
            assert "business_overview" in result
            assert "search_results" in result
            assert "error" in result["search_results"]  # Error in search results
            assert "Failed to initialize client" in result["business_overview"]  # Error in chat
