.PHONY: help install test lint format type-check check clean run

# Default target
help:
	@echo "Available commands:"
	@echo "  make install      - Install all dependencies"
	@echo "  make test         - Run all tests with pytest"
	@echo "  make lint         - Run flake8 linter"
	@echo "  make format       - Format code with black"
	@echo "  make format-check - Check code formatting without changes"
	@echo "  make type-check   - Run mypy type checker"
	@echo "  make check        - Run all checks (format-check + lint + type-check + test)"
	@echo "  make fix          - Auto-fix issues (format + lint)"
	@echo "  make clean        - Remove cache and build files"
	@echo "  make run          - Run the application"

# Install dependencies
install:
	@echo "Installing dependencies with Poetry..."
	poetry install

# Run tests
test:
	@echo "Running tests with pytest..."
	poetry run pytest tests/ -v --cov=backend --cov-report=term-missing

# Run quick tests (without coverage)
test-quick:
	@echo "Running quick tests..."
	poetry run pytest tests/ -v

# Run flake8 linter
lint:
	@echo "Running flake8 linter..."
	poetry run flake8 backend/ tests/ main.py --count --statistics

# Format code with black
format:
	@echo "Formatting code with black..."
	poetry run black backend/ tests/ main.py

# Check code formatting (without making changes)
format-check:
	@echo "Checking code formatting with black..."
	poetry run black --check backend/ tests/ main.py

# Run mypy type checker
type-check:
	@echo "Running mypy type checker..."
	poetry run mypy backend/ main.py

# Run all checks (format-check, lint, type-check, test)
check: format-check lint type-check test
	@echo ""
	@echo "✅ All checks passed!"

# Auto-fix issues (format + lint autofixes)
fix: format
	@echo "Auto-fixing complete!"

# Clean cache and build files
clean:
	@echo "Cleaning cache and build files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	rm -rf build/ dist/ .tox/ htmlcov/
	@echo "Clean complete!"

# Run the application
run:
	@echo "Running application..."
	poetry run app

# Install pre-commit hook (optional)
install-hooks:
	@echo "Installing git pre-commit hook..."
	@echo '#!/bin/sh' > .git/hooks/pre-commit
	@echo 'make check' >> .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit
	@echo "Pre-commit hook installed!"

# CI/CD target - runs all checks without stopping on first failure
ci: format-check
	@echo "Running lint..."
	-poetry run flake8 backend/ tests/ main.py --count --statistics
	@echo "Running type-check..."
	-poetry run mypy backend/ main.py
	@echo "Running tests..."
	-poetry run pytest tests/ -v --cov=backend --cov-report=term-missing
	@echo "CI checks complete!"
