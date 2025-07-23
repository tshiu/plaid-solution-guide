# Solution Guide Generator

Transform call transcripts into technical solution guides using AI-powered research and sophisticated prompt engineering.

## 🎯 What This Does

The Solution Guide Generator takes call transcripts from customer conversations and automatically generates comprehensive, technical solution guides. It:

1. **Researches companies** using Glean's APIs to understand their business model and technical needs
2. **Analyzes transcripts** to extract key requirements and use cases  
3. **Generates guides** using sophisticated prompts based on successful examples
4. **Provides actionable** technical implementation details for sales engineers

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- uv package manager
- Glean API access (instance URL and API token)

### Installation

1. **Clone and navigate to the project:**

   ```bash
   cd solution-guide-generator
   ```

2. **Install dependencies:**

   ```bash
   uv sync
   ```

3. **Set up environment variables:**

   ```bash
   cp ../.env.example .env
   # Edit .env with your Glean credentials:
   # GLEAN_INSTANCE=your-glean-instance
   # GLEAN_API_TOKEN=your-api-token
   ```

4. **Run the application:**

   ```bash
   uv run uvicorn app.main:app --reload
   ```

5. **Open your browser:** <http://localhost:8000>

## 💻 Usage

### Web Interface

1. **Enter company name** (e.g., "TechCorp")
2. **Paste call transcript** from your customer conversation
3. **Add optional context** (use case, technical requirements, etc.)
4. **Click "Generate Solution Guide"**
5. **Copy the generated guide** to your clipboard

### API Usage

You can also use the REST API directly:

```bash
curl -X POST "http://localhost:8000/api/v1/generate-guide" \
     -H "Content-Type: application/json" \
     -d '{
       "company_name": "TechCorp",
       "transcript": "Call transcript content here...",
       "additional_context": "They need payment processing integration"
     }'
```

### Example Input/Output

**Input:**

- Company: "TechCorp"  
- Transcript: Technical demo call discussing financial technology requirements
- Context: "Building fintech platform with bank connectivity and payment processing integration"

**Output:**

- Complete technical solution guide with implementation details
- Specific API recommendations and code examples
- Integration roadmap and next steps
- Answers to questions raised in the call

## 🏗️ Architecture

### Project Structure

```
solution-guide-generator/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── models/                 # Pydantic request/response models
│   │   ├── requests.py
│   │   └── responses.py
│   ├── services/              # Business logic services
│   │   ├── glean_client.py    # Glean API integration
│   │   ├── prompt_builder.py  # LLM prompt generation
│   │   └── guide_generator.py # Main orchestration service
│   ├── routers/               # API route handlers
│   │   └── api.py
│   └── static/                # Web interface
│       └── index.html
├── tests/                     # Unit tests
├── pyproject.toml            # Project configuration
└── README.md                 # This file
```

### How It Works

1. **Company Research:** Uses Glean's search and chat APIs to gather business context
2. **Use Case Extraction:** Analyzes transcript to identify technical requirements  
3. **Prompt Engineering:** Builds sophisticated prompts based on successful examples
4. **Guide Generation:** Uses Glean's chat API to generate the final solution guide
5. **Post-Processing:** Validates and formats the output for consistency

## 🔧 Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app

# Run specific test file
uv run pytest tests/test_glean_client.py
```

### Code Formatting

```bash
# Format code
uv run ruff format .

# Check for issues  
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check . --fix
```

### Environment Validation

Test your configuration:

```bash
curl -X POST "http://localhost:8000/api/v1/validate-environment"
```

### Development Server

```bash
# Run with auto-reload
uv run uvicorn app.main:app --reload --log-level debug

# Run on different port
uv run uvicorn app.main:app --port 8080
```

## 📝 Configuration

### Environment Variables

Create a `.env` file with these required variables:

```bash
GLEAN_INSTANCE=your-glean-instance     # Your Glean instance URL (without https://)
GLEAN_API_TOKEN=your-api-token         # Your Glean API token
DEBUG=true                             # Enable debug mode (optional)
LOG_LEVEL=INFO                         # Logging level (optional)
```

### Configuration Details

- **GLEAN_INSTANCE**: The base URL of your Glean instance (e.g., "company.glean.com")
- **GLEAN_API_TOKEN**: Your Glean API authentication token
- **DEBUG**: Enables debug mode with detailed error messages and API docs
- **LOG_LEVEL**: Controls logging verbosity (DEBUG, INFO, WARNING, ERROR)

## 🧪 Testing

The project includes comprehensive unit tests covering:

- **Glean API integration** (mocked external calls)
- **Prompt generation** (template validation and content)
- **Guide generation** (end-to-end workflow)
- **Error handling** (network failures, invalid inputs)
- **Data processing** (transcript analysis, post-processing)

### Test Coverage

```bash
# Generate coverage report
uv run pytest --cov=app --cov-report=html

# View coverage in browser
open htmlcov/index.html
```

## 📊 API Endpoints

### Core Endpoints

- `POST /api/v1/generate-guide` - Generate a solution guide from transcript
- `POST /api/v1/validate-environment` - Check configuration and connectivity
- `POST /api/v1/research-company` - Research a company without generating a guide
- `GET /api/v1/health` - API health check
- `GET /health` - Application health check

### API Documentation

When running in debug mode, visit:

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>

## 🎨 Features

### ✅ Implemented Features

- **Web Interface**: Clean, responsive UI for easy use
- **Company Research**: Automatic research using Glean APIs
- **Smart Prompting**: Sophisticated prompt engineering based on successful examples
- **Guide Generation**: AI-powered solution guide creation
- **Error Handling**: Comprehensive error handling and validation
- **Testing**: Full unit test coverage
- **Documentation**: Extensive code documentation and user guides

### 🚧 Future Enhancements

1. **Template System**: Multiple guide templates for different use cases
2. **Export Options**: PDF, Word, and email integration
3. **Version Control**: Save and compare different guide versions
4. **Batch Processing**: Handle multiple transcripts at once
5. **Analytics**: Track usage patterns and guide effectiveness
6. **Integration**: Direct CRM integration for seamless workflow

## 🐛 Troubleshooting

### Common Issues

**Environment validation fails:**

- Check your `.env` file exists and has correct values
- Verify Glean instance URL doesn't include `https://`
- Confirm API token has correct permissions

**Application won't start:**

- Ensure Python 3.13+ is installed
- Run `uv sync` to install dependencies
- Check for port conflicts (default: 8000)

**API calls fail:**

- Verify network connectivity to Glean instance
- Check API token hasn't expired
- Review logs for detailed error messages

### Debug Mode

Enable debug mode for detailed error information:

```bash
# In .env file
DEBUG=true
LOG_LEVEL=DEBUG

# Then restart the application
uv run uvicorn app.main:app --reload
```

## 🤝 Contributing

### Development Workflow

1. **Create a feature branch**
2. **Make changes** with comprehensive tests
3. **Run the test suite**: `uv run pytest`
4. **Format code**: `uv run ruff format .`
5. **Check for issues**: `uv run ruff check .`
6. **Submit for review**

### Code Standards

- Follow **Google-style docstrings**
- Use **type annotations** throughout
- Maintain **test coverage** above 90%
- Follow **PEP 8** style guidelines (enforced by ruff)
- Write **descriptive commit messages**

## 📄 License

This project is intended for internal use. See your organization's software licensing policies for details.

---

## 🆘 Support

For technical support or questions:

1. **Check this README** for common solutions
2. **Review the logs** for detailed error information  
3. **Test API connectivity** using the validation endpoint
4. **Contact your technical team** for Glean API access issues

---

*Built with ❤️ using Python 3.13, FastAPI, and modern development practices.*

## Key Dependencies

### Core Technologies
- **FastAPI**: Modern, fast web framework for building APIs
- **Python 3.13**: Latest Python with enhanced performance and type hints
- **Pydantic**: Data validation and settings management with type annotations
- **Official Glean SDK**: Using `glean-api-client` for reliable API interactions

### Development & Testing
- **UV**: Fast Python package manager for dependency management
- **Pytest**: Comprehensive testing framework with async support
- **Ruff**: Lightning-fast Python linter and formatter

### API Integration
- **Glean Enterprise Search**: Official `glean-api-client` SDK for:
  - Company research via search API
  - AI-powered chat interactions
  - Built-in retry logic and error handling
  - Type-safe API responses
