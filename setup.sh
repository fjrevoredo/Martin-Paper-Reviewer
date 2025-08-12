#!/bin/bash

# Martin Setup Script
# This script sets up the development environment using uv (preferred) or venv

set -e

echo "Setting up Martin development environment..."

# Check if uv is available
if command -v uv &> /dev/null; then
    echo "Using uv for dependency management..."
    
    # Create virtual environment with uv
    uv venv
    
    # Activate virtual environment
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source .venv/Scripts/activate
    else
        source .venv/bin/activate
    fi
    
    # Install dependencies with uv
    uv pip install -e ".[dev]"
    
    echo "✅ Environment setup complete with uv!"
    echo "To activate the environment, run:"
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        echo "  source .venv/Scripts/activate"
    else
        echo "  source .venv/bin/activate"
    fi
    
elif command -v python3 &> /dev/null; then
    echo "uv not found, using venv..."
    
    # Create virtual environment with venv
    python3 -m venv .venv
    
    # Activate virtual environment
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source .venv/Scripts/activate
    else
        source .venv/bin/activate
    fi
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    pip install -e ".[dev]"
    
    echo "✅ Environment setup complete with venv!"
    echo "To activate the environment, run:"
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        echo "  source .venv/Scripts/activate"
    else
        echo "  source .venv/bin/activate"
    fi
    
else
    echo "❌ Neither uv nor python3 found. Please install Python 3.8+ or uv."
    exit 1
fi

echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and add your OpenAI API key"
echo "2. Run: martin 'https://arxiv.org/pdf/1706.03762.pdf'"