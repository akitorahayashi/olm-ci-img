# ==============================================================================
# justfile for Ollama CI Image Builder
# ==============================================================================

set dotenv-load

# Ensure DOCKERHUB_USERNAME is set in .env or environment variables
DOCKER_USER := env("DOCKERHUB_USERNAME", "")

default: help

# Show usage instructions and list all available recipes
help:
    @echo "Usage: just [recipe]"
    @echo "Available recipes:"
    @just --list | tail -n +2 | awk '{printf "  \033[36m%-20s\033[0m %s\n", $1, substr($0, index($0, $2))}'

# ==============================================================================
# Environment Setup
# ==============================================================================

# Install Python dependencies with uv and create .env file if needed
setup:
	@echo "Installing python dev dependencies with uv..."
	@uv sync
	@echo "Creating environment file..."
	@if [ ! -f .env ] && [ -f .env.example ]; then \
		echo "Creating .env from .env.example..."; \
		cp .env.example .env; \
		echo "✅ Environment file created (.env)"; \
	else \
		echo ".env already exists. Skipping creation."; \
	fi
	@echo "💡 Please edit the .env file and set your DOCKERHUB_USERNAME."

# ==============================================================================
# TESTING
# ==============================================================================

# Run full pytest suite
test: 
    just unit-test 
    just e2e-test

# Run unit tests only
unit-test:
    @echo "Running pytest unit tests..."
    uv run pytest tests/test_unit.py

# Run end-to-end tests only
e2e-test:
    @echo "Running pytest end-to-end tests..."
    uv run pytest tests/e2e/


# ==============================================================================
# CODE QUALITY
# ==============================================================================

# Format code with black and ruff --fix
format:
    @echo "Formatting code with black and ruff..."
    @uv run black .
    @uv run ruff check . --fix

# Lint code with black check and ruff
lint:
    @echo "Linting code with black check and ruff..."
    @uv run black --check .
    @uv run ruff check .
    
# ==============================================================================
# CLEANUP
# ==============================================================================

# Remove __pycache__ and .venv to make project lightweight
clean:
    @echo "🧹 Cleaning up project..."
    @find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    @rm -rf .venv
    @rm -rf .pytest_cache
    @rm -rf .ruff_cache
    @rm -rf .uv-cache
    @rm -f test_db.sqlite3
    @echo "✅ Cleanup completed"
