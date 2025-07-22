# Repository Context for AI Coding Agents

## 🎯 Project Overview

This repository contains a **Plaid Solution Guide Generator** - a web application that analyzes call transcripts and generates technical solution guides using Glean's AI capabilities. The application helps Plaid sales engineers create customized technical documentation for prospective clients.

## 📁 Repository Structure

```plaintext
explore/                                    # Root workspace directory
├── solution-guide-generator/               # Main application (Python 3.13 + FastAPI)
│   ├── app/                               # Application source code
│   │   ├── main.py                        # FastAPI application entry point
│   │   ├── config.py                      # Environment configuration (Pydantic)
│   │   ├── models/                        # Request/response models
│   │   │   ├── requests.py                # Input validation models
│   │   │   └── responses.py               # API response models
│   │   ├── services/                      # Business logic layer
│   │   │   ├── glean_client.py            # Glean API integration
│   │   │   ├── guide_generator.py         # Main orchestration service
│   │   │   └── prompt_builder.py          # LLM prompt engineering
│   │   ├── routers/                       # API route definitions
│   │   │   └── api.py                     # REST API endpoints
│   │   └── static/                        # Frontend assets
│   │       └── index.html                 # Web interface
│   ├── tests/                             # Comprehensive unit tests
│   │   ├── test_glean_client.py           # Glean API client tests
│   │   ├── test_guide_generator.py        # Business logic tests
│   │   └── test_prompt_builder.py         # Prompt engineering tests
│   ├── pyproject.toml                     # Project dependencies & config
│   ├── .env.example                       # Environment variables template
│   └── README.md                          # Application documentation
├── solutions-guides/                      # Generated solution guides
│   └── example-guide.md                   # Example: Sample solution guide
├── transcripts/                           # Call transcript storage
│   └── tracey/
│       └── example-call.txt               # Example transcript
├── run-solution-guide-generator.sh        # Launch script
├── Makefile                               # Development commands
├── IMPLEMENTATION_PLAN.md                 # Original implementation plan
└── pyproject.toml                         # Workspace configuration
```

## 🏗️ Architecture

### **Technology Stack**

- **Backend**: Python 3.13 + FastAPI + Pydantic
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **AI Integration**: Glean API for company research and LLM generation
- **Testing**: pytest with async support
- **Code Quality**: ruff for linting and formatting
- **Package Management**: uv (fast Python package manager)

### **Key Components**

1. **`GleanClient`** (`app/services/glean_client.py`)
   - Handles all Glean API interactions
   - Company search and AI chat functionality
   - Robust error handling and logging

2. **`GuideGenerator`** (`app/services/guide_generator.py`)
   - Main orchestration service
   - Coordinates research, prompt building, and guide generation
   - Post-processes generated content for quality

3. **`PromptBuilder`** (`app/services/prompt_builder.py`)
   - LLM prompt engineering
   - Uses example guide as style template
   - Builds contextual prompts for consistent output

4. **Web Interface** (`app/static/index.html`)
   - Simple form-based UI
   - Real-time feedback and loading states
   - Copy-to-clipboard functionality

## 🔧 Development Workflow

### **Quick Start Commands**

```bash
# From root directory
make install          # Install dependencies
make run              # Start development server
make test             # Run test suite
make lint             # Check code quality
```

### **Environment Setup**

1. Copy `solution-guide-generator/.env.example` to `solution-guide-generator/.env`
2. Configure Glean credentials:

   ```bash
   GLEAN_INSTANCE=your-glean-instance
   GLEAN_API_TOKEN=your-api-token
   ```

### **Testing Strategy**

- **Unit Tests**: 29 tests covering all major components
- **Mocking**: Extensive use of `unittest.mock` for external APIs
- **Async Testing**: Full async/await support with `pytest-asyncio`
- **Coverage**: 55% overall coverage focusing on business logic

## 🎨 Code Style & Standards

### **Python Standards**

- **Type Annotations**: Required throughout (`from __future__ import annotations`)
- **Docstrings**: Google-style docstrings for all public methods
- **Error Handling**: Comprehensive try/catch with proper logging
- **Async/Await**: Used consistently for I/O operations

### **Code Quality Tools**

- **ruff**: Linting and formatting (configured in `pyproject.toml`)
- **pytest**: Testing framework with coverage reporting
- **Pydantic**: Data validation and settings management

### **Key Patterns**

- **Dependency Injection**: Services injected into routes
- **Configuration Management**: Centralized in `config.py` with lazy loading
- **Error Responses**: Standardized error handling with proper HTTP codes
- **Logging**: Structured logging throughout the application

## 🔗 API Integration

### **Glean API Usage**

- **Company Search**: `/api/search` endpoint for company research
- **AI Chat**: `/api/chat` endpoint for guided content generation
- **Authentication**: Bearer token authentication
- **Rate Limiting**: Built-in retry logic and error handling

### **API Endpoints**

```plaintext
POST /api/v1/generate-guide   # Main guide generation
GET  /api/v1/health           # Health check
POST /api/v1/validate-env     # Environment validation
POST /api/v1/research-company # Company research only
```

## 🧪 Testing Guidelines

### **Running Tests**

```bash
# All tests
cd solution-guide-generator && uv run pytest tests/ -v

# Specific test file
uv run pytest tests/test_glean_client.py -v

# With coverage
uv run pytest --cov=app --cov-report=term-missing
```

### **Test Structure**

- **Fixtures**: Shared test setup in each test class
- **Mocking**: External API calls mocked for reliability
- **Async Testing**: All async methods properly tested
- **Edge Cases**: Error conditions and boundary cases covered

## 🚀 Deployment Considerations

### **Environment Variables**

- `GLEAN_INSTANCE`: Your Glean instance URL
- `GLEAN_API_TOKEN`: Glean API authentication token
- `DEBUG`: Development mode toggle (default: False)
- `LOG_LEVEL`: Logging verbosity (default: INFO)

### **Production Readiness**

- ✅ Comprehensive error handling
- ✅ Input validation with Pydantic
- ✅ Structured logging
- ✅ Health check endpoints
- ✅ CORS configuration
- ✅ Static file serving

## 🤖 AI Agent Guidelines

### **When Making Changes**

1. **Run Tests First**: Always verify current state with `make test`
2. **Check Code Quality**: Use `make lint` before committing
3. **Update Documentation**: Keep README and docstrings current
4. **Test Integration**: Verify Glean API integration works

### **Common Tasks**

- **Adding Features**: Follow the service-based architecture pattern
- **API Changes**: Update both models and tests
- **UI Updates**: Modify `app/static/index.html`
- **Configuration**: Add new settings to `app/config.py`

### **Debugging Tips**

- **Logs**: Check application logs for detailed error information
- **Environment**: Use `make validate-env` to check configuration
- **API Testing**: Use the web interface or direct API calls
- **Mocking**: Tests use extensive mocking - check mock setup for failures

## 📚 Key Files to Understand

1. **`app/main.py`**: Application entry point and configuration
2. **`app/services/guide_generator.py`**: Main business logic
3. **`solutions-guides/`**: Templates and examples for generated guides
4. **`tests/`**: Comprehensive test suite for all components
5. **`Makefile`**: Development workflow automation

## 🔍 Troubleshooting

### **Common Issues**

- **Environment**: Ensure `.env` file is properly configured
- **Dependencies**: Run `uv sync` if imports fail
- **Tests**: Check that mock objects are properly configured
- **API**: Verify Glean credentials and instance URL

### **Getting Help**

- Check the comprehensive README in `solution-guide-generator/`
- Review test files for usage examples
- Use `make help` for available commands
- Examine the IMPLEMENTATION_PLAN.md for original architecture decisions
