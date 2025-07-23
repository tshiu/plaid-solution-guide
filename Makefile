# Makefile for Plaid Solution Guide Generator
# Run from the root explore directory

.PHONY: help install dev test lint format clean run stop logs validate-env

# Default target
help:
	@echo "🚀 Plaid Solution Guide Generator - Available Commands:"
	@echo ""
	@echo "📦 Setup & Installation:"
	@echo "  make install      - Install all dependencies"
	@echo "  make dev          - Install development dependencies"
	@echo ""
	@echo "🔧 Development:"
	@echo "  make run          - Start the application (development mode)"
	@echo "  make test         - Run all tests"
	@echo "  make lint         - Check code quality with ruff"
	@echo "  make format       - Format code with ruff"
	@echo "  make validate-env - Check environment configuration"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  make clean        - Clean up build artifacts"
	@echo "  make logs         - Show recent application logs"
	@echo ""
	@echo "💡 Quick Start:"
	@echo "  1. make install"
	@echo "  2. Configure solution-guide-generator/.env"
	@echo "  3. make run"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	uv sync
	@echo "✅ Dependencies installed!"

# Install development dependencies  
dev: install
	@echo "🔧 Setting up development environment..."
	uv sync --dev --project solution-guide-generator
	@echo "✅ Development environment ready!"

# Start the application
run:
	@echo "🚀 Starting Solution Guide Generator..."
	@if [ ! -f ".env" ]; then \
		echo "❌ Please create .env with your Glean credentials."; \
		exit 1; \
	fi
	@echo "🌟 Starting server at http://localhost:8000"
	uv run --project solution-guide-generator uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
test:
	@echo "🧪 Running tests..."
	cd solution-guide-generator && GLEAN_INSTANCE=test-instance GLEAN_API_TOKEN=test-token uv run pytest tests/ -v
	@echo "✅ All tests passed!"

# Lint code
lint:
	@echo "🔍 Checking code quality..."
	cd solution-guide-generator && uv run ruff check .
	@echo "✅ Code quality check passed!"

# Format code
format:
	@echo "🎨 Formatting code..."
	cd solution-guide-generator && uv run ruff format .
	cd solution-guide-generator && uv run ruff check . --fix
	@echo "✅ Code formatted!"

# Validate environment
validate-env:
	@echo "🔧 Validating environment..."
	@if [ ! -f "solution-guide-generator/.env" ]; then \
		echo "❌ .env file not found in solution-guide-generator/"; \
		echo "   Create it from .env.example and add your Glean credentials"; \
		exit 1; \
	fi
	cd solution-guide-generator && uv run python -c "from app.config import get_settings; s=get_settings(); print(f'✅ Config loaded: {s.glean_instance}')"
	@echo "✅ Environment validation passed!"

# Clean build artifacts
clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleanup complete!"

# Show application logs (when running in background)
logs:
	@echo "📋 Recent application activity..."
	@echo "💡 Tip: Run 'make run' to start the application in foreground mode"

# Stop application (if running in background)
stop:
	@echo "🛑 Stopping application..."
	@pkill -f "uvicorn app.main:app" || echo "No running application found"
	@echo "✅ Application stopped!" 