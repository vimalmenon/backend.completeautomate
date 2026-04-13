.PHONY: help install test lint format format-all isort-check type-check check clean run deadcode

PY_SOURCES = backend/ tests/ main.py
NOTEBOOK_SOURCES = main.ipynb

# Default target
help:
	@echo "Available commands:"
	@echo "  make install      - Install all dependencies"
	@echo "  make test         - Run all tests with pytest"
	@echo "  make lint         - Run flake8 linter"
	@echo "  make format       - Format code with black"
	@echo "  make format-all   - Run black + ruff --fix + isort on project sources"
	@echo "  make format-check - Check code formatting without changes"
	@echo "  make isort-check  - Check import ordering with isort"
	@echo "  make type-check   - Run mypy type checker"
	@echo "  make check        - Run all checks (format-check + isort-check + lint + type-check + test)"
	@echo "  make fix          - Auto-fix issues (format + lint)"
	@echo "  make deadcode     - Find dead code using deadcode analyzer"
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
	poetry run flake8 $(PY_SOURCES) --count --statistics --exclude=venv,.venv

# Format code with black
format:
	@echo "Formatting code with black..."
	poetry run black $(PY_SOURCES)

# Check code formatting (without making changes)
format-check:
	@echo "Checking code formatting with black..."
	poetry run black --check $(PY_SOURCES)

# Format and auto-fix linting/imports for entire project
format-all:
	@echo "Running black, ruff --fix, and isort on project sources..."
	poetry run black $(PY_SOURCES)
	poetry run ruff check --fix $(PY_SOURCES)
	poetry run isort $(PY_SOURCES) $(NOTEBOOK_SOURCES)

# Check import ordering
isort-check:
	@echo "Checking import order with isort..."
	poetry run isort --check-only $(PY_SOURCES) $(NOTEBOOK_SOURCES)

# Run mypy type checker
type-check:
	@echo "Running mypy type checker..."
	poetry run mypy backend/ main.py

# Run all checks (format-check, isort-check, lint, type-check, test)
check: format-check isort-check lint type-check test
	@echo ""
	@echo "✅ All checks passed!"

# Auto-fix issues (format + lint autofixes)
fix: format-all
	@echo "Auto-fixing complete!"

# Find dead code using deadcode analyzer
deadcode:
	@echo "Analyzing dead code..."
	poetry run deadcode backend/ main.py

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
	@echo "Running isort-check..."
	-poetry run isort --check-only $(PY_SOURCES) $(NOTEBOOK_SOURCES)
	@echo "Running lint..."
	-poetry run flake8 $(PY_SOURCES) --count --statistics --exclude=venv,.venv
	@echo "Running type-check..."
	-poetry run mypy backend/ main.py
	@echo "Running tests..."
	-poetry run pytest tests/ -v --cov=backend --cov-report=term-missing
	@echo "CI checks complete!"
