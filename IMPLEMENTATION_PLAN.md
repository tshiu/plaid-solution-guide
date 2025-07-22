# Solution Guide Generator - Implementation Plan

## Project Overview

### Purpose

Build a web application to help sales engineers automatically generate customized solution guides from call transcripts. The app will:

1. Accept call transcripts, company names, and additional context
2. Research companies using Glean's APIs
3. Generate tailored solution guides similar to the IntelXLabs example
4. Provide a clean, maintainable codebase for future enhancements

### Target Users

- Sales engineers who need to quickly create technical solution guides
- Anyone who needs to transform call transcripts into structured technical documentation

### Why This Architecture

- **Python 3.13**: Latest features, better performance, modern type hints
- **FastAPI**: Excellent for APIs, automatic documentation, type validation
- **Glean Integration**: Leverages existing company research capabilities
- **Modular Design**: Easy to test, maintain, and extend

---

## Technical Architecture

### Core Components

```
solution-guide-generator/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── models/                 # Pydantic models for request/response
│   ├── services/              # Business logic
│   │   ├── glean_client.py    # Glean API integration
│   │   ├── prompt_builder.py  # LLM prompt generation
│   │   └── guide_generator.py # Solution guide creation
│   ├── routers/               # API route handlers
│   └── static/                # Frontend assets
├── tests/                     # Unit and integration tests
├── docs/                     # Documentation
├── .env.example              # Environment variable template
└── pyproject.toml           # Project configuration
```

### Technology Stack

- **Web Framework**: FastAPI (modern, fast, automatic API docs)
- **Package Manager**: uv (fastest Python package manager)
- **Linting/Formatting**: ruff (extremely fast, comprehensive)
- **Testing**: pytest (industry standard, excellent plugins)
- **Environment**: python-dotenv (secure configuration management)
- **HTTP Requests**: httpx (async-first, modern requests library)

---

## Implementation Steps

### Phase 1: Project Setup & Infrastructure

#### Step 1.1: Initialize Project Structure

```bash
# Create project directory and basic structure
mkdir solution-guide-generator
cd solution-guide-generator

# Initialize with uv
uv init
```

**Why uv**: Fastest Python package manager, excellent dependency resolution, built-in virtual environment management.

#### Step 1.2: Configure pyproject.toml

```toml
[project]
name = "solution-guide-generator"
version = "0.1.0"
description = "Generate solution guides from call transcripts using Glean API"
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.5.0",
    "httpx>=0.25.0",
    "python-dotenv>=1.0.0",
    "jinja2>=3.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
]

[tool.ruff]
target-version = "py313"
line-length = 88
select = ["E", "F", "I", "N", "W", "UP"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

**Why these dependencies**:

- FastAPI: Modern web framework with automatic API documentation
- Pydantic: Data validation with Python type hints
- httpx: Async HTTP client for external API calls
- python-dotenv: Secure environment variable management

#### Step 1.3: Environment Configuration

Create `.env.example`:

```
GLEAN_INSTANCE=your-glean-instance
GLEAN_API_TOKEN=your-api-token
DEBUG=true
LOG_LEVEL=INFO
```

### Phase 2: Core Application Structure

#### Step 2.1: Create Pydantic Models (`app/models/`)

**File: `app/models/requests.py`**

```python
from pydantic import BaseModel, Field
from typing import Optional

class TranscriptRequest(BaseModel):
    """Request model for generating solution guides from transcripts."""
    
    transcript: str = Field(..., min_length=1, description="Call transcript content")
    company_name: str = Field(..., min_length=1, description="Target company name")
    additional_context: Optional[str] = Field(None, description="Extra context about the use case")
    
    class Config:
        json_schema_extra = {
            "example": {
                "transcript": "Call transcript content here...",
                "company_name": "TechCorp Inc",
                "additional_context": "They're looking to implement payment processing"
            }
        }
```

**Why Pydantic**: Automatic request validation, type safety, generates OpenAPI schemas.

#### Step 2.2: Glean Client Service (`app/services/glean_client.py`)

```python
import httpx
from typing import Dict, List, Any, Optional
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class GleanClient:
    """Client for interacting with Glean APIs."""
    
    def __init__(self):
        """Initialize Glean client with configuration."""
        self.base_url = f"https://{settings.glean_instance}"
        self.headers = {
            "Authorization": f"Bearer {settings.glean_api_token}",
            "Content-Type": "application/json"
        }
    
    async def search_company(self, company_name: str) -> Dict[str, Any]:
        """Search for company information using Glean."""
        # Implementation details here
    
    async def chat_query(self, message: str, context: Optional[List[str]] = None) -> str:
        """Query Glean chat for additional insights."""
        # Implementation details here
```

**Why async**: Non-blocking API calls, better performance for I/O operations.

#### Step 2.3: Prompt Builder Service (`app/services/prompt_builder.py`)

```python
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class PromptBuilder:
    """Builds prompts for generating solution guides."""
    
    def build_solution_guide_prompt(
        self,
        transcript: str,
        company_name: str,
        company_research: Dict[str, Any],
        additional_context: Optional[str] = None
    ) -> str:
        """
        Build a comprehensive prompt for generating solution guides.
        
        Args:
            transcript: Call transcript content
            company_name: Target company name
            company_research: Research data from Glean
            additional_context: Optional additional context
            
        Returns:
            Formatted prompt string for LLM
        """
        # Detailed prompt construction based on IntelXLabs example
```

**Why separate prompt builder**: Easier to test, modify, and version control prompts.

### Phase 3: API Routes & Web Interface

#### Step 3.1: API Routes (`app/routers/api.py`)

```python
from fastapi import APIRouter, HTTPException, Depends
from app.models.requests import TranscriptRequest
from app.services.guide_generator import GuideGenerator
import logging

router = APIRouter(prefix="/api/v1", tags=["solution-guides"])
logger = logging.getLogger(__name__)

@router.post("/generate-guide")
async def generate_solution_guide(request: TranscriptRequest):
    """
    Generate a solution guide from call transcript.
    
    Args:
        request: Transcript request containing company info and transcript
        
    Returns:
        Generated solution guide in markdown format
    """
    try:
        generator = GuideGenerator()
        guide = await generator.generate_guide(
            transcript=request.transcript,
            company_name=request.company_name,
            additional_context=request.additional_context
        )
        return {"guide": guide}
    except Exception as e:
        logger.error(f"Error generating guide: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate guide")
```

#### Step 3.2: Web Interface (`app/static/index.html`)

```html
<!DOCTYPE html>
<html>
<head>
    <title>Solution Guide Generator</title>
    <style>/* Clean, modern CSS */</style>
</head>
<body>
    <div class="container">
        <h1>Solution Guide Generator</h1>
        <form id="guideForm">
            <div class="form-group">
                <label for="company">Company Name:</label>
                <input type="text" id="company" required>
            </div>
            <div class="form-group">
                <label for="transcript">Call Transcript:</label>
                <textarea id="transcript" required></textarea>
            </div>
            <div class="form-group">
                <label for="context">Additional Context (Optional):</label>
                <textarea id="context"></textarea>
            </div>
            <button type="submit">Generate Solution Guide</button>
        </form>
        <div id="result"></div>
    </div>
    <script>/* JavaScript for form handling */</script>
</body>
</html>
```

### Phase 4: Testing Strategy

#### Step 4.1: Unit Tests (`tests/`)

```python
# tests/test_glean_client.py
import pytest
from unittest.mock import AsyncMock, patch
from app.services.glean_client import GleanClient

@pytest.mark.asyncio
async def test_search_company():
    """Test company search functionality."""
    client = GleanClient()
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value.json.return_value = {"results": []}
        result = await client.search_company("TestCorp")
        assert isinstance(result, dict)

# tests/test_prompt_builder.py
from app.services.prompt_builder import PromptBuilder

def test_build_solution_guide_prompt():
    """Test prompt building with various inputs."""
    builder = PromptBuilder()
    prompt = builder.build_solution_guide_prompt(
        transcript="Test transcript",
        company_name="TestCorp",
        company_research={},
        additional_context="Test context"
    )
    assert "TestCorp" in prompt
    assert "Test transcript" in prompt
```

**Why comprehensive testing**: Ensures reliability, catches regressions, documents expected behavior.

### Phase 5: LLM Prompt Engineering

#### Step 5.1: Solution Guide Generation Prompt

Based on the successful IntelXLabs approach, create a structured prompt:

```python
SOLUTION_GUIDE_PROMPT_TEMPLATE = """
You are an expert sales engineer creating technical solution guides. 

Based on this call transcript from {company_name} and research data, generate a concise, 
technical solution guide following this exact format and style:

TRANSCRIPT:
{transcript}

COMPANY RESEARCH:
{company_research}

ADDITIONAL CONTEXT:
{additional_context}

Generate a solution guide that:
1. Focuses on technical implementation details
2. Avoids business jargon 
3. Uses clear, scannable formatting
4. Includes specific API calls and code examples where relevant
5. Addresses questions raised in the call
6. Provides actionable next steps

Follow the structure and tone of this example:
[Include condensed version of IntelXLabs guide as example]

Generate the guide for {company_name} now:
"""
```

### Phase 6: Configuration & Documentation

#### Step 6.1: Configuration Management (`app/config.py`)

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    glean_instance: str
    glean_api_token: str
    debug: bool = False
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

#### Step 6.2: User Documentation (`README.md`)

```markdown
# Solution Guide Generator

## Quick Start

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Configure environment:**

   ```bash
   cp .env.example .env
   # Edit .env with your Glean credentials
   ```

3. **Run the application:**

   ```bash
   uv run uvicorn app.main:app --reload
   ```

4. **Open browser:** <http://localhost:8000>

## Usage Guide

### Web Interface

1. Enter company name
2. Paste call transcript
3. Add optional context
4. Click "Generate Solution Guide"

### API Usage

```bash
curl -X POST "http://localhost:8000/api/v1/generate-guide" \
     -H "Content-Type: application/json" \
     -d '{"transcript": "...", "company_name": "...", "additional_context": "..."}'
```

## Development

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
uv run ruff format .
uv run ruff check .
```

```

---

## Implementation Order

### Day 1: Foundation
1. Set up project structure with uv
2. Configure pyproject.toml with dependencies
3. Create basic FastAPI app with health check
4. Set up environment configuration

### Day 2: Core Services
1. Implement Glean client with basic API calls
2. Create Pydantic models for requests/responses
3. Build prompt builder service
4. Add basic error handling

### Day 3: API & Integration
1. Create API routes for guide generation
2. Integrate all services in guide generator
3. Add comprehensive logging
4. Test end-to-end flow

### Day 4: Frontend & UX
1. Build clean web interface
2. Add JavaScript for async form submission
3. Implement progress indicators
4. Style with modern CSS

### Day 5: Testing & Documentation
1. Write comprehensive unit tests
2. Add integration tests
3. Create user documentation
4. Set up development workflows

---

## Success Criteria

- [ ] Application starts without errors
- [ ] Can accept transcript input via web form
- [ ] Successfully calls Glean APIs
- [ ] Generates coherent solution guides
- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] Clear documentation for non-programmers

---

## Future Enhancements

1. **Template System**: Multiple guide templates for different use cases
2. **Export Options**: PDF, Word, email integration
3. **Version Control**: Save and compare different guide versions
4. **Batch Processing**: Handle multiple transcripts at once
5. **Analytics**: Track usage patterns and guide effectiveness

---

This plan provides a solid foundation for building a maintainable, well-documented application that can grow with your needs while following Python best practices.
