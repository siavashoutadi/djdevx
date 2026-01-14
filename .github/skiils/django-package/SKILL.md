---
name: django package
description: Guide for adding support for new django packages to djdevx
---

# Adding new Django packages

This skill helps you add support for new django packages to djdevx.

## When to use this skill

Use this skill when you need to:
- Create a new django package support

## Creating packages

1. Review the [django packages directory](djdevx/backend/django/packages) to understand the structure of packages and the commands they support. How typer is used to create the cli command lines. How user is prompted to provide the input needed for the packages. Also notice that some packages have different backends.
2. Review the [templates diretory](djdevx/templates/django) to understand how the templates are structured and how the variables are created for user input using jinja2 templating.
3. Review the [tests directory](tests/backend/django/packages) to undrestand how the tests are structured and how the data is provided.
4. Find the documentation for the package in internet or ask for the link to understand how to install and configure the package.
5. Create the the stucture for the new django package in [django packages directory](djdevx/backend/django/packages) and add the typer code for install/remove/env. Also import the new typer package in djdevx/backend/django/packages/__init__.py.
6. Add the required templates needed such as settings and urls in [templates diretory](djdevx/templates/django).
7. Add proper test in [tests directory](tests/backend/django/packages) to test the package structure is correct and the content match the expected data.
8. Run the test to ensure nothing broke.

## Running tests

To run tests locally:
```bash
uv run pytest -v
```

## Best practices

- NEVER add one line comments for the logic added.
- Follow best practices for python.
- Never skip the steps.
