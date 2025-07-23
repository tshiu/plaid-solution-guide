# Plaid Solutions Exploration Workspace

This workspace contains tools and applications for exploring Plaid's financial API solutions, including a **Solution Guide Generator** that creates technical documentation from call transcripts.

## 🚀 Quick Start

### 1. Setup

```bash
# Install dependencies
make install

# Configure environment
cp solution-guide-generator/.env.example solution-guide-generator/.env
# Edit .env with your Glean credentials
```

### 2. Run the Application

```bash
# Start the solution guide generator
make run

# Or use the shell script
./run-solution-guide-generator.sh
```

The application will be available at **<http://localhost:8000>**

### 3. Generate a Solution Guide

1. Open the web interface
2. Paste a call transcript
3. Enter the company name
4. Add any additional context
5. Click "Generate Guide"

## 📁 What's in This Workspace

### 🛠️ [Solution Guide Generator](./solution-guide-generator/)

**Main Application** - FastAPI web app that generates technical solution guides from call transcripts using Glean's AI.

- **Language**: Python 3.13
- **Framework**: FastAPI + Pydantic
- **AI Integration**: Glean API
- **Testing**: 29 unit tests with pytest
- **Frontend**: Clean HTML/CSS/JS interface

### 📋 [Solution Guides](./solutions-guides/)

**Generated Output** - Collection of generated solution guides for different companies.

- **Example**: Sample technical solution guides for client engagements
- **Format**: Markdown with technical details and implementation guidance

### 📞 [Transcripts](./transcripts/)

**Input Data** - Call transcripts used to generate solution guides.

- **Structure**: Organized by sales engineer name
- **Format**: Plain text transcripts

## 🔧 Available Commands

### Quick Commands

```bash
make help              # Show all available commands
make run               # Start the application
make test              # Run all tests
make lint              # Check code quality
```

### Development Commands

```bash
make dev               # Setup development environment
make format            # Format code
make clean             # Clean build artifacts
make validate-env      # Check configuration
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Interface                            │
│                  (HTML + JavaScript)                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  FastAPI Backend                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│
│  │    API      │ │   Business  │ │       Services          ││
│  │   Routes    │ │    Logic    │ │  (Glean Integration)    ││
│  └─────────────┘ └─────────────┘ └─────────────────────────┘│
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   Glean API                                │
│           (Company Research + AI Generation)               │
└─────────────────────────────────────────────────────────────┘
```

## 📖 Documentation

- **[CONTEXT.md](./CONTEXT.md)** - Comprehensive guide for AI coding agents
- **[IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md)** - Original implementation plan
- **[Application README](./solution-guide-generator/README.md)** - Detailed app documentation

## 🔐 Configuration

### Required Environment Variables

Create `solution-guide-generator/.env` with:

```bash
GLEAN_INSTANCE=your-glean-instance
GLEAN_API_TOKEN=your-api-token
DEBUG=false
LOG_LEVEL=INFO
```

### Optional Configuration

- **DEBUG**: Enable development mode
- **LOG_LEVEL**: Set logging verbosity (DEBUG, INFO, WARNING, ERROR)

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific test files
cd solution-guide-generator
uv run pytest tests/test_glean_client.py -v

# With coverage report
uv run pytest --cov=app --cov-report=term-missing
```

## 🚨 Troubleshooting

### Common Issues

**Application won't start:**

- Check `.env` file configuration
- Verify Glean credentials
- Run `make validate-env`

**Tests failing:**

- Ensure dependencies are installed: `make install`
- Check Python version: requires Python 3.13+

**Import errors:**

- Run `uv sync` to install dependencies
- Check virtual environment activation

### Getting Help

1. **Check logs**: Application provides detailed error messages
2. **Validate environment**: `make validate-env`
3. **Review documentation**: See `solution-guide-generator/README.md`
4. **Run diagnostics**: `make test` to verify everything works

## 🔄 Development Workflow

### Adding New Features

1. **Code changes**: Follow the service-based architecture
2. **Add tests**: Write unit tests for new functionality
3. **Check quality**: Run `make lint` and `make format`
4. **Verify**: Run `make test` to ensure everything works

### Working with AI Agents

- **Context**: Review `CONTEXT.md` for repository understanding
- **Standards**: Follow existing patterns and code style
- **Testing**: Always run tests before and after changes
- **Documentation**: Keep README and docstrings updated

## 📊 Project Status

- ✅ **Core Application**: Fully functional solution guide generator
- ✅ **Testing**: Comprehensive test suite (29 tests)
- ✅ **Code Quality**: Linted and formatted with ruff
- ✅ **Documentation**: Complete developer and user docs
- ✅ **Deployment**: Production-ready with proper error handling

## 🤝 Contributing

1. **Setup**: Run `make dev` for development environment
2. **Code**: Follow existing patterns and add tests
3. **Quality**: Use `make lint` and `make format`
4. **Test**: Verify with `make test`
5. **Document**: Update relevant documentation

---

## 💡 Example Usage

**Input**: Call transcript discussing client's financial technology needs

**Output**: Technical solution guide with:

- ✅ Plaid product recommendations (Link, Auth, Transactions)
- ✅ Implementation flow and code examples
- ✅ Security and compliance considerations
- ✅ Getting started instructions

**Time**: ~30 seconds from transcript to polished guide

---

_Built with ❤️ for Plaid Sales Engineering_
