#!/bin/bash

# Solution Guide Generator - Launch Script
# This script configures and launches the Plaid solution guide generator from the root directory

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -d "solution-guide-generator" ]; then
    print_error "This script must be run from the root explore directory"
    exit 1
fi

print_status "🚀 Starting Solution Guide Generator..."

# Check if .env file exists in the solution-guide-generator directory
if [ ! -f "solution-guide-generator/.env" ]; then
    print_warning "No .env file found in solution-guide-generator/"
    print_status "Creating .env file from template..."
    
    if [ -f "solution-guide-generator/.env.example" ]; then
        cp solution-guide-generator/.env.example solution-guide-generator/.env
        print_warning "Please edit solution-guide-generator/.env with your actual Glean credentials:"
        print_warning "  - GLEAN_INSTANCE=your-instance"
        print_warning "  - GLEAN_API_TOKEN=your-token"
        echo
        read -p "Press Enter after you've configured the .env file, or Ctrl+C to exit..."
    else
        print_error ".env.example file not found. Please create solution-guide-generator/.env manually."
        exit 1
    fi
fi

# Sync dependencies
print_status "📦 Syncing dependencies..."
uv sync

# Change to the solution-guide-generator directory
cd solution-guide-generator

# Run the application
print_success "🌟 Launching Solution Guide Generator at http://localhost:8000"
print_status "Press Ctrl+C to stop the server"
echo

# Run with development settings
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 