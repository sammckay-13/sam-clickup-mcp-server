# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Test Commands
- Run server: `uv run clickup-mcp-server`
- Run tests: `pytest`
- Run single test: `pytest tests/test_client.py::TestClickUpClient::test_get_workspaces`
- Lint code: `ruff check .`
- Type checking: `pyright`

## Code Style Guidelines
- Python 3.10+ with type hints using standard library typing module
- Use Pydantic for data models and validation
- Class naming: PascalCase (e.g., `ClickUpClient`)
- Function/method naming: snake_case (e.g., `get_workspaces`)
- Variables: snake_case
- Constants: UPPER_SNAKE_CASE
- Imports order: standard library, third-party, local
- Error handling: Use appropriate exception types with descriptive messages
- Documentation: Use docstrings for classes and functions
- Prefer composition over inheritance
- Use logging for diagnostics (not print statements)
- For API requests, always validate inputs before sending
- Keep code modular and follow single responsibility principle