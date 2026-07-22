---
name: update-prek-versions
description: >
  Updates prek hook versions in .pre-commit-config.yaml to their latest
  available versions.
license: MIT
compatibility: opencode
metadata:
  audience: developers
  workflow: dependency-management
---

## Task

Update prek hook versions in `.pre-commit-config.yaml` to their latest versions.

## Steps

1. Update hook versions in `.pre-commit-config.yaml`:

   ```bash
   uv run prek update
   ```

2. Review the changes:

   ```bash
   git diff .pre-commit-config.yaml
   ```

3. Install the updated hooks:

   ```bash
   uv run prek install --prepare-hooks
   ```

4. Run all hooks against all files to verify the new versions don't introduce failures:

   ```bash
   uv run prek run --all-files
   ```

5. Clean up old cached hook environments:

   ```bash
   uv run prek cache gc
   ```
