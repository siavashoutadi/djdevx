# CI/CD & Releases

`djdevx` ships two GitHub Actions workflows that run the test suite on every
push and produce a GitHub Release when a version tag is pushed. The repository
itself is managed with **uv**; pixi only appears inside generated target Django
projects at runtime.

## Workflows

### `ci.yml` — continuous testing

- Triggered on every `push` to any branch and on every `pull_request`.
- Runs on `ubuntu-latest` with Python 3.14 and installs both **uv** and
  **pixi** (pixi is required at runtime by the tests that scaffold target
  Django projects).
- Steps: install uv + pixi, `uv sync --group dev` then `uv run pytest`.
- This is the safety net that ensures nothing is broken before a merge or
  tag.

### `release.yml` — build on tag push

- Triggered on `push` of any tag matching `v*` (e.g. `v0.2.0`).
- Job `test`: identical to CI (runs the full test suite).
- Job `build` (`needs: test`): only runs if tests pass, then:
  - `uv build` produces the sdist and wheel in `dist/`. The built version is
    derived from the tag (see [Versioning](#versioning)).
  - `softprops/action-gh-release` creates a GitHub Release and attaches
    `dist/*` as release assets.
- No PyPI or GitHub Packages publishing — release artifacts are provided as a
  GitHub Release only.

## Versioning

The package version is derived from git tags via
[hatch-vcs](https://github.com/ofek/hatch-vcs).

- `pyproject.toml` declares `dynamic = ["version"]` with
  `[tool.hatch.version] source = "vcs"` and a build hook that writes the
  resolved version into `djdevx/_version.py`.
- `djdevx/_version.py` is the single version file; `djdevx/__init__.py` reads
  `__version__` from it. The committed file carries a dev fallback
  (`0.1.0+dev`) — a build from a tag overwrites it with the tag's version.
- Source checkouts and `uv run` reflect a development version
  (e.g. `0.1.0.dev0+g<sha>`), while builds from a tag use the tagged version
  exactly.

## Releasing

1. Ensure `main` is green (CI passes).
2. Tag the release commit and push it:

   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```

3. GitHub Actions runs the tests, and if they pass, builds the package and
   creates the GitHub Release with the wheel and sdist attached.
4. The next development cycle starts automatically: the working tree between
   releases reports the next dev version (`0.2.1.dev0`) with no manual bump.
   Do **not** edit `djdevx/_version.py` to bump versions — the tag is the
   single source of truth.
