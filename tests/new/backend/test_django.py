from pathlib import Path
import tomllib
import yaml
from typer.testing import CliRunner
from djdevx.main import app

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "django"


def test_new_django_backend(temp_dir):
    """
    Test that the CLI creates a new Django backend project successfully.
    """
    result = runner.invoke(
        app,
        [
            "new",
            "backend",
            "django",
            "--project-name",
            "my_django_project",
            "--project-description",
            "A sample Django backend project",
            "--project-directory",
            str(temp_dir),
            "--python-version",
            "3.14",
            "--backend-root",
            "backend",
        ],
    )

    assert result.exit_code == 0

    expected_files = [
        f.relative_to(DATA_DIR) for f in DATA_DIR.rglob("*") if f.is_file()
    ]

    exlude_files = [
        Path("backend/pyproject.toml"),
        Path(".pre-commit-config.yaml"),
        Path("backend/.environments/dev"),
        Path(".devcontainer/.env/devcontainer"),
    ]

    for relative_path in expected_files:
        created_file = temp_dir / relative_path

        assert created_file.exists(), f"Missing file: {relative_path}"
        if relative_path in exlude_files:
            continue
        expected_content = (DATA_DIR / relative_path).read_text()
        actual_content = created_file.read_text()

        assert actual_content == expected_content, (
            f"Content mismatch in file: {relative_path}"
        )

    pyproject_path = temp_dir / "backend" / "pyproject.toml"
    assert pyproject_path.exists(), "pyproject.toml file not created"

    with open(pyproject_path, "rb") as f:
        pyproject_data = tomllib.load(f)

    project = pyproject_data["project"]
    assert project["name"] == "my_django_project"
    assert project["description"] == "A sample Django backend project"
    assert project["version"] == "0.1.0"
    assert project["requires-python"] == ">=3.14"
    assert project["readme"] == "README.md"

    required_dependencies = [
        "django",
        "django-environ",
        "django-redis",
        "django-typer",
        "ipdb",
        "ipython",
        "psycopg2-binary",
        "uvicorn",
    ]

    required_dev_dependencies = [
        "django-upgrade",
        "factory-boy",
        "pre-commit",
        "rich",
        "ruff",
    ]

    project_dependencies = [
        dep.split(">")[0]
        .split("<")[0]
        .split("=")[0]
        .split("!")[0]
        .split("~")[0]
        .strip()
        for dep in project["dependencies"]
    ]

    print(project_dependencies)

    project_dev_dependencies = [
        dep.split(">")[0]
        .split("<")[0]
        .split("=")[0]
        .split("!")[0]
        .split("~")[0]
        .strip()
        for dep in pyproject_data["dependency-groups"]["dev"]
    ]

    for dep in required_dependencies:
        assert dep in project_dependencies, f"Required dependency '{dep}' not found"

    for dep in required_dev_dependencies:
        assert dep in project_dev_dependencies, (
            f"Required dev dependency '{dep}' not found"
        )

    precommit_config_path = temp_dir / ".pre-commit-config.yaml"
    assert precommit_config_path.exists(), ".pre-commit-config.yaml file not created"

    with open(precommit_config_path, "r") as f:
        precommit_config = yaml.safe_load(f)

    assert "repos" in precommit_config
    repos = precommit_config["repos"]

    expected_repos = [
        "https://github.com/pre-commit/pre-commit-hooks",
        "https://github.com/astral-sh/ruff-pre-commit",
        "https://github.com/asottile/pyupgrade",
        "https://github.com/adamchainz/django-upgrade",
        "https://github.com/adamchainz/djade-pre-commit",
        "https://github.com/sirwart/ripsecrets",
        "https://github.com/shellcheck-py/shellcheck-py",
    ]

    repo_urls = [repo["repo"] for repo in repos]

    for expected_repo in expected_repos:
        assert expected_repo in repo_urls, (
            f"Expected repo '{expected_repo}' not found in pre-commit config"
        )

    precommit_hooks_repo = next(
        (
            repo
            for repo in repos
            if repo["repo"] == "https://github.com/pre-commit/pre-commit-hooks"
        ),
        None,
    )
    assert precommit_hooks_repo is not None

    expected_hook_ids = [
        "trailing-whitespace",
        "end-of-file-fixer",
        "check-yaml",
        "check-added-large-files",
        "check-merge-conflict",
        "check-case-conflict",
    ]

    actual_hook_ids = [hook["id"] for hook in precommit_hooks_repo["hooks"]]

    for hook_id in expected_hook_ids:
        assert hook_id in actual_hook_ids, (
            f"Expected hook '{hook_id}' not found in pre-commit-hooks"
        )

    ruff_repo = next(
        (
            repo
            for repo in repos
            if repo["repo"] == "https://github.com/astral-sh/ruff-pre-commit"
        ),
        None,
    )
    assert ruff_repo is not None

    ruff_hook_ids = [hook["id"] for hook in ruff_repo["hooks"]]
    assert "ruff" in ruff_hook_ids, "ruff linter hook not found"
    assert "ruff-format" in ruff_hook_ids, "ruff formatter hook not found"

    django_upgrade_repo = next(
        (
            repo
            for repo in repos
            if repo["repo"] == "https://github.com/adamchainz/django-upgrade"
        ),
        None,
    )
    assert django_upgrade_repo is not None

    django_upgrade_hook = django_upgrade_repo["hooks"][0]
    assert django_upgrade_hook["id"] == "django-upgrade"
    assert "args" in django_upgrade_hook
    assert "--target-version" in django_upgrade_hook["args"]

    djade_repo = next(
        (
            repo
            for repo in repos
            if repo["repo"] == "https://github.com/adamchainz/djade-pre-commit"
        ),
        None,
    )
    assert djade_repo is not None

    djade_hook = djade_repo["hooks"][0]
    assert djade_hook["id"] == "djade"
    assert "args" in djade_hook
    assert "--target-version" in djade_hook["args"]
