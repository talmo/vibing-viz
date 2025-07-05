#!/bin/bash
# Development environment setup for vibing-viz

set -e  # Exit on error

echo "Setting up vibing-viz development environment..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.12"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 12) else 1)"; then
    echo "Error: Python 3.12+ is required. Found: $python_version"
    exit 1
fi

# Install uv if not present
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add to PATH for current session
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Create virtual environment and install dependencies
echo "Creating virtual environment..."
uv venv

echo "Installing dependencies..."
uv sync --all-extras

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
uv run pre-commit install

echo ""
echo "✅ Development environment ready!"
echo ""
echo "To activate the environment:"
echo "  source .venv/bin/activate"
echo ""
echo "Common commands:"
echo "  uv run pytest              # Run tests"
echo "  uv run black .             # Format code"
echo "  uv run ruff check --fix .  # Fix linting issues"
echo ""