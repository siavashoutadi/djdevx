---
name: update-package-versions
description: >
  Updates Python package versions in pyproject.toml to the latest available
  versions on PyPI.
license: MIT
compatibility: opencode
metadata:
  audience: developers
  workflow: dependency-management
---

## Task

Update Python package dependencies in `pyproject.toml` to their latest versions.

## Steps

1. Read `pyproject.toml` and identify dependencies under `[project.dependencies]` and `[dependency-groups]`.

   Use `tomlkit` (project dependency) to parse:

   ```python
   from pathlib import Path
   import tomlkit
   doc = tomlkit.parse(Path("pyproject.toml").read_text())
   deps = doc["project"]["dependencies"]
   ```

   Or run `uv export --format=requirements` to list the current pinned versions.

2. For each dependency, fetch the latest stable version using the helper script:

   ```bash
   uv run .agents/skills/update-package-versions/scripts/get_latest_package_version.py <PACKAGE_NAME>
   ```

3. Install the latest version:

   ```bash
   uv add <DEPENDENCY>==<LATEST_VERSION>
   ```

4. Run tests to verify:

   ```bash
   uv run pytest
   ```

## Rules

- Only update to stable releases (the helper script already filters pre-release versions).
- Run the full test suite after all version bumps.
- If a test fails after a version bump, check the package's changelog for breaking changes.
