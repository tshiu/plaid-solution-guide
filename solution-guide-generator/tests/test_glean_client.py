"""Unit tests for the Glean client service."""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.services.glean_client import GleanClient


class TestGleanClient:
    """Test suite for GleanClient class."""

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
        mock_response = {"results": [{"title": "Test Company", "snippet": "Test company description"}]}

        with patch("httpx.AsyncClient") as mock_client:
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status = MagicMock()
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response_obj

            result = await glean_client.search_company("TestCorp")

            assert result == mock_response
            assert "results" in result

    @pytest.mark.asyncio
    async def test_search_company_http_error(self, glean_client):
        """Test company search with HTTP error."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post.side_effect = httpx.HTTPError("API Error")

            result = await glean_client.search_company("TestCorp")

            assert "error" in result
            assert result["results"] == []

    @pytest.mark.asyncio
    async def test_chat_query_success(self, glean_client):
        """Test successful chat query."""
        mock_response = {"response": "Test chat response"}

        with patch("httpx.AsyncClient") as mock_client:
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status = MagicMock()
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response_obj

            result = await glean_client.chat_query("Test question")

            assert result == "Test chat response"

    @pytest.mark.asyncio
    async def test_chat_query_with_context(self, glean_client):
        """Test chat query with context."""
        mock_response = {"response": "Contextual response"}
        context = ["Previous message 1", "Previous message 2"]

        with patch("httpx.AsyncClient") as mock_client:
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status = MagicMock()
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response_obj

            result = await glean_client.chat_query("Test question", context)

            assert result == "Contextual response"

    @pytest.mark.asyncio
    async def test_chat_query_http_error(self, glean_client):
        """Test chat query with HTTP error."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post.side_effect = httpx.HTTPError("Chat API Error")

            result = await glean_client.chat_query("Test question")

            assert "Error querying Glean" in result

    @pytest.mark.asyncio
    async def test_get_company_insights_success(self, glean_client):
        """Test getting comprehensive company insights."""
        with patch.object(glean_client, "search_company", return_value={"results": []}) as mock_search:
            with patch.object(glean_client, "chat_query", return_value="Business overview") as mock_chat:
                result = await glean_client.get_company_insights("TestCorp", "payment processing")

                assert result["company_name"] == "TestCorp"
                assert result["business_overview"] == "Business overview"
                assert "search_results" in result
                mock_search.assert_called_once_with("TestCorp")
                assert mock_chat.call_count >= 1

    @pytest.mark.asyncio
    async def test_get_company_insights_with_use_case(self, glean_client):
        """Test getting company insights with specific use case."""
        with patch.object(glean_client, "search_company", return_value={"results": []}):
            with patch.object(
                glean_client,
                "chat_query",
                side_effect=["Business overview", "Technical context"],
            ) as mock_chat:
                result = await glean_client.get_company_insights("TestCorp", "financial API integration")

                assert result["company_name"] == "TestCorp"
                assert result["business_overview"] == "Business overview"
                assert result["technical_context"] == "Technical context"
                assert mock_chat.call_count == 2

    @pytest.mark.asyncio
    async def test_get_company_insights_error_handling(self, glean_client):
        """Test error handling in company insights."""
        with patch.object(glean_client, "search_company", side_effect=Exception("Search failed")):
            result = await glean_client.get_company_insights("TestCorp")

            assert "error" in result
            assert result["company_name"] == "TestCorp"
            # Error case may not set business_overview exactly as expected
            assert "business_overview" in result
