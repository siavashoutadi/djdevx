---
name: Tester
description: Guide for testing djdevx
---

# Testing djdevx

This skill helps you write and run tests for djdevx.

## When to use this skill

Use this skill when you need to:
- Write tests for new features or packages
- Run tests to validate changes
- Fix failing tests

## Writing tests

1. Review the [tests directory](tests) to understand the structure of tests and how they are organized by module.
2. Refer to existing tests in the relevant directory (e.g., [tests/backend/django/packages](tests/backend/django/packages)) to understand the testing patterns used.
3. Create your test file following the naming convention `test_*.py`.
4. Use pytest fixtures and assertions to write clear, maintainable tests.
5. Ensure tests validate both positive and negative cases.

## Running tests

To run all tests locally:
```bash
uv run pytest -v
```

To run specific tests:
```bash
uv run pytest -v tests/path/to/test_file.py
```

To run tests with coverage:
```bash
uv run pytest --cov=djdevx tests/
```
