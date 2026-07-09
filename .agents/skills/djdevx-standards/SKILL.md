---
name: djdevx-standards
description: >
  Project-wide code standards and best practices for the djdevx Python project.
  Use this skill as a reference for coding style, technology stack, and conventions.
license: MIT
compatibility: opencode
metadata:
  audience: developers
  workflow: coding-standards
---

All code standards and conventions are documented in the project's developer documentation. See the following files under `docs/`:

- **Code Standards (primary reference)**: [docs/developer-guide/code-standards.md](../../../docs/developer-guide/code-standards.md) — technology stack, project structure, package/CLI/template/testing conventions, config & tracking, console output, code quality
- **Architecture**: [docs/developer-guide/architecture.md](../../../docs/developer-guide/architecture.md) — high-level system overview
- **CLI Architecture**: [docs/developer-guide/cli-architecture.md](../../../docs/developer-guide/cli-architecture.md) — command tree, Typer patterns, registering sub-commands
- **Package Architecture**: [docs/developer-guide/package-architecture.md](../../../docs/developer-guide/package-architecture.md) — BasePackage, lifecycle hooks, path derivation, sub-package groups
- **Template System**: [docs/developer-guide/template-system.md](../../../docs/developer-guide/template-system.md) — Jinja2 rendering, TemplateManager, InstallParam
- **Testing Guide**: [docs/developer-guide/testing.md](../../../docs/developer-guide/testing.md) — test patterns, fixtures, markers, CLI integration tests
- **Creating a Package**: [docs/developer-guide/creating-a-package.md](../../../docs/developer-guide/creating-a-package.md) — step-by-step guide with examples
- **Deployment Architecture**: [docs/developer-guide/deployment-architecture.md](../../../docs/developer-guide/deployment-architecture.md) — BaseDeployPlugin and adding new targets

All documentation lives in the `docs/` directory at the project root.
