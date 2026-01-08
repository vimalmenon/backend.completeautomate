# Copilot Instructions

## Project Context
- This is the backend for Complete Automate.
- Use Python 3.13+ style and preserve existing architecture.
- Prefer small, focused changes over broad refactors.

## Python Environment
- Always use the existing repository virtual environment at `.venv`.
- Do not create a new virtual environment unless explicitly requested.
- Use relative paths only (no absolute paths).
- Reuse the interpreter from `.venv/Scripts/python.exe` (Windows) or `.venv/bin/python` (Linux/macOS/WSL).
- Install missing packages into this existing `.venv` only when needed.

## Code Style
- Follow existing code style in each file.
- Keep function and variable names descriptive.
- Do not add new dependencies unless required.
- Handle errors with `AppException` where appropriate.

## Testing
- Add or update focused tests for behavior changes.
- Prefer running targeted tests first, then broader tests.

## Scope Rules
- Implement only what is requested.
- Do not modify unrelated files.
- Avoid breaking public interfaces unless explicitly requested.
