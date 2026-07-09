# /// script
# dependencies = []
# ///

import sys
import json
import re
import urllib.request
import urllib.error


def _is_prerelease(version):
    return bool(re.search(r"(a|alpha|b|beta|rc|c|pre|preview|dev)", version, re.I))


def _sort_key(version):
    return [int(p) if p.isdigit() else p for p in re.split(r"(\d+)", version)]


def get_latest_stable_version(package_name):
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Package '{package_name}' not found.")
            return None
        raise

    releases = data.get("releases", {})
    stable_versions = [v for v in releases if releases[v] and not _is_prerelease(v)]
    if not stable_versions:
        print(f"No stable release found for '{package_name}'.")
        return None

    stable_versions.sort(key=_sort_key)
    return stable_versions[-1]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python get_latest_package_version.py <package_name>")
        sys.exit(1)
    package = sys.argv[1]
    version = get_latest_stable_version(package)
    if version:
        print(f"Latest stable version of '{package}' is {version}")
