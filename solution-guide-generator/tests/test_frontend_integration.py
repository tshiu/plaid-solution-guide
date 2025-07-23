"""Simple integration tests to verify frontend-backend communication."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestFrontendIntegration:
    """Test frontend-backend integration points."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_guide_generator(self):
        """Mock guide generator for testing."""
        with patch("app.routers.api.GuideGenerator") as mock:
            mock_instance = AsyncMock()
            mock.return_value = mock_instance
            yield mock_instance

    def test_api_response_structure_matches_frontend_expectations(self, client, mock_guide_generator):
        """Test that API response structure matches what frontend JavaScript expects."""
        # Mock the guide generation to return a sample guide
        mock_guide_content = """# Sample Solution Guide

## Overview
This is a test solution guide for TestCorp.

## Key Features
- Feature 1
- Feature 2

## Implementation
```python
# Sample code
def hello_world():
    return "Hello, TestCorp!"
```

## Next Steps
1. Step one
2. Step two
"""

        mock_guide_generator.generate_guide = AsyncMock(return_value=mock_guide_content)

        # Make request that matches frontend
        request_data = {
            "transcript": "Test call transcript with customer",
            "company_name": "TestCorp",
            "additional_context": "They need payment processing",
        }

        response = client.post("/api/v1/generate-guide", json=request_data)

        # Verify response structure
        assert response.status_code == 200
        data = response.json()

        # Verify the field names match what frontend expects
        assert "guide" in data  # Frontend now expects 'guide' field
        assert "company_name" in data
        assert "metadata" in data

        # Verify content
        assert data["guide"] == mock_guide_content
        assert data["company_name"] == "TestCorp"
        assert data["metadata"]["generated_successfully"] is True

    def test_frontend_can_handle_api_errors(self, client, mock_guide_generator):
        """Test that API errors are properly formatted for frontend consumption."""
        # Mock an error in guide generation
        mock_guide_generator.generate_guide = AsyncMock(side_effect=Exception("Simulated API error"))

        request_data = {"transcript": "Test transcript", "company_name": "ErrorCorp"}

        response = client.post("/api/v1/generate-guide", json=request_data)

        # Verify error response structure
        assert response.status_code == 500
        data = response.json()

        # Frontend expects 'detail' field for errors
        assert "detail" in data
        assert "Failed to generate solution guide" in data["detail"]

    def test_markdown_content_structure(self, client, mock_guide_generator):
        """Test that returned markdown has proper structure for rendering."""
        # Test with various markdown elements
        mock_guide_content = """# Test Company Solution Guide

## Executive Summary
This is a **bold** statement with *emphasis*.

## Technical Requirements
- Requirement 1
- Requirement 2
  - Sub-requirement 2.1
  - Sub-requirement 2.2

## Code Example
```python
def process_payment(amount, currency="USD"):
    return {"amount": amount, "currency": currency}
```

## Implementation Timeline
| Phase | Duration | Tasks |
|-------|----------|-------|
| 1 | 2 weeks | Setup |
| 2 | 4 weeks | Development |

> **Note**: This is a blockquote with important information.

### Next Steps
1. First step
2. Second step
3. Final step
"""

        mock_guide_generator.generate_guide = AsyncMock(return_value=mock_guide_content)

        request_data = {"transcript": "Detailed transcript", "company_name": "MarkdownCorp"}

        response = client.post("/api/v1/generate-guide", json=request_data)

        assert response.status_code == 200
        data = response.json()

        guide_content = data["guide"]

        # Verify markdown structure elements are present
        assert "# Test Company Solution Guide" in guide_content
        assert "## Executive Summary" in guide_content
        assert "**bold**" in guide_content
        assert "*emphasis*" in guide_content
        assert "```python" in guide_content
        assert "| Phase | Duration | Tasks |" in guide_content
        assert "> **Note**:" in guide_content
        assert "1. First step" in guide_content

    def test_frontend_health_check(self, client):
        """Test that health check endpoint works for frontend monitoring."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert "static_files" in data
        assert "version" in data

    def test_api_validation_matches_frontend_form(self, client):
        """Test that API validation matches frontend form requirements."""
        # Test empty transcript (frontend requires this)
        response = client.post("/api/v1/generate-guide", json={"transcript": "", "company_name": "TestCorp"})
        assert response.status_code == 422  # Pydantic validation error

        # Test empty company name
        response = client.post("/api/v1/generate-guide", json={"transcript": "Valid transcript", "company_name": ""})
        assert response.status_code == 422  # Pydantic validation error

        # Test missing required fields
        response = client.post(
            "/api/v1/generate-guide",
            json={
                "transcript": "Valid transcript"
                # Missing company_name
            },
        )
        assert response.status_code == 422  # Pydantic validation error
