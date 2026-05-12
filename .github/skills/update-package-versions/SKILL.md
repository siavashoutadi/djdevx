---
name: update-package-versions
description: Guide for updating Python package versions in djdevx in pyproject.toml to the latest versions.
---

Perform these actions in sequence.

1- Read the pyproject.toml and find all dependencies
2- Fetch the latest version for the dependencies using .github/skills/update-package-versions/scripts/get_latest_package_version.py script

```bash
uv run scripts/get_latest_package_version.py <PACKAGE_NAME>.
```

3- Use `uv add <DEPENDENCY>==<LATEST_VERSION>`
4- Run the tests using `uv run pytest` and make sure all tests are successful
