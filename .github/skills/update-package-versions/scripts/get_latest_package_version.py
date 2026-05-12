# /// script
# dependencies = [
#   "requests",
# ]
# ///

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
        print("Usage: python get_latest_package_version.py <package_name>")
        sys.exit(1)
    package = sys.argv[1]
    version = get_latest_version(package)
    if version:
        print(f"Latest version of '{package}' is {version}")
