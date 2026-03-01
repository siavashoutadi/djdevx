---
name: update-package-versions
description: To update the dependecies in pyproject.toml to the latest versions.
---

Perform these actions in sequence.
- Read the pyproject.toml and find all dependencies
- Fetch the latest version for the dependencies using this script. create ./.ai-agents/package_update/get_latest_version.py and run it using `uv run --with requests ./.ai-agents/package_update/get_latest_version.py <PACKAGE_NAME>`.

```python
import sys
import requests

def get_latest_version(package_name):
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Package '{package_name}' not found.")
        return None
    data = response.json()
    return data["info"]["version"]

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python get_latest_version.py <package_name>")
        sys.exit(1)
    package = sys.argv[1]
    version = get_latest_version(package)
    if version:
        print(f"Latest version of '{package}' is {version}")
```

- Use `uv add <DEPENDENCY>==<LATEST_VERSION>`
- Run the tests using `uv run pytest` and make sure all tests are successful
