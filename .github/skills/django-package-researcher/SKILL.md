---
name: Django Package Researcher
description: Guide for researching Django packages from the internet
---

# Researching Django Packages from the Internet

This skill helps you research and gather information about Django packages from the internet using an autonomous agent. It searches for documentation on ReadTheDocs, GitHub, and PyPI, and provides installation and configuration guidance.

## When to use this skill

Use this skill when you need to:
- Find documentation for a Django package (e.g., django-htmx, django-cors-headers)
- Understand how to install and configure a package
- Gather package-specific requirements and setup steps
- Research package features and dependencies
- Avoid cluttering your main session context with research tasks

## How it works

The skill uses a subagent to:
1. Search for the package on ReadTheDocs (preferred), GitHub, or PyPI
2. Fetch and analyze package documentation
3. Extract installation instructions
4. Identify configuration requirements (settings, middleware, URLs, etc.)
5. Return a structured summary with key information

## Using the skill

When researching a package, use the `runSubagent` function with this prompt:

```
You are researching a Django package [PACKAGE_NAME] to understand how to integrate it with djdevx.

Your task:
1. Search for the package documentation, preferring ReadTheDocs over GitHub and PyPI
2. Fetch the documentation pages and extract:
   - Installation instructions
   - Required configuration (settings.py additions, middleware, installed_apps, URLs, etc.)
   - Any special requirements or dependencies
   - Key features relevant to integration
3. Provide a comprehensive summary including:
   - Package name and purpose
   - Installation command (pip/uv)
   - Settings configuration required
   - Middleware setup (if applicable)
   - URL configuration (if applicable)
   - Environment variables (if applicable)
   - Any special setup steps
   - Links to documentation used

Return ONLY the structured information without any explanation of the research process.
```

## Example usage

### Research django-htmx:
```
You are researching a Django package 'django-htmx' to understand how to integrate it with djdevx.

Your task:
1. Search for the package documentation, preferring ReadTheDocs over GitHub and PyPI
2. Fetch the documentation pages and extract:
   - Installation instructions
   - Required configuration (settings.py additions, middleware, installed_apps, URLs, etc.)
   - Any special requirements or dependencies
   - Key features relevant to integration
3. Provide a comprehensive summary including:
   - Package name and purpose
   - Installation command (pip/uv)
   - Settings configuration required
   - Middleware setup (if applicable)
   - URL configuration (if applicable)
   - Environment variables (if applicable)
   - Any special setup steps
   - Links to documentation used

Return ONLY the structured information without any explanation of the research process.
```

## What you'll get back

The subagent will return structured information but with all details so it can be implemented.

```
Package: django-htmx
Purpose: Django view decorators and utilities for HTMX integration

Installation:
- Command: pip install django-htmx
- No special dependencies

Settings Configuration:
- INSTALLED_APPS: 'django_htmx'

INSTALLED_APPS = [
    ...,
    "django_htmx",
    ...,
]

- Middleware: required

MIDDLEWARE = [
    ...,
    "django_htmx.middleware.HtmxMiddleware",
    ...,
]

- Special settings: required

{% load django_htmx %}
 <!doctype html>
 <html>
   <head>
     ...
     {% htmx_script %}
   </head>
   <body hx-headers='{"x-csrftoken": "{{ csrf_token }}"}'>
     ...
   </body>
 </html>


URL Configuration: None

Documentation: https://django-htmx.readthedocs.io/
```
