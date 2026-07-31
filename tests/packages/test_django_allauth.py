from pathlib import Path
import os
from typer.testing import CliRunner
from djdevx.main import app
from djdevx.utils.project.pixi_runner import PixiRunner
from tests.test_helpers import create_test_django_project

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "django_allauth"


def test_django_allauth_account_install_and_remove(temp_dir):
    """
    Test django-allauth account package installation and removal.
    """

    create_test_django_project(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "packages",
            "add",
            "django-allauth",
            "--provider",
            "account",
        ],
    )

    assert result.exit_code == 0, f"Install failed: {result.output}"

    settings_file = temp_dir / "settings" / "packages" / "django_allauth_account.py"
    assert settings_file.exists(), "Settings file not created"

    urls_file = temp_dir / "urls" / "packages" / "django_allauth_account.py"
    assert urls_file.exists(), "URLs file not created"

    auth_app_file = temp_dir / "authentication" / "__init__.py"
    assert auth_app_file.exists(), "Authentication app __init__.py not created"

    auth_apps_file = temp_dir / "authentication" / "apps.py"
    assert auth_apps_file.exists(), "Authentication apps.py not created"

    assert PixiRunner().has_dependency("django-allauth"), (
        "django-allauth dependency not found after installation"
    )

    data_account_dir = DATA_DIR / "account"
    for expected_file in data_account_dir.rglob("*"):
        if expected_file.is_file():
            relative_path = expected_file.relative_to(data_account_dir)
            actual_file = temp_dir / relative_path

            assert actual_file.exists(), f"Expected file {relative_path} not created"

            expected_content = expected_file.read_text()
            actual_content = actual_file.read_text()
            assert actual_content == expected_content, (
                f"Content mismatch in {relative_path}"
            )

    os.chdir(temp_dir)
    result = runner.invoke(
        app,
        [
            "packages",
            "remove",
            "django-allauth",
            "--provider",
            "account",
        ],
    )

    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not settings_file.exists(), "Settings file not removed"
    assert not urls_file.exists(), "URLs file not removed"
    assert not auth_app_file.parent.exists(), "Authentication directory not removed"

    data_account_dir = DATA_DIR / "account"
    for expected_file in data_account_dir.rglob("*"):
        if expected_file.is_file():
            relative_path = expected_file.relative_to(data_account_dir)
            actual_file = temp_dir / relative_path
            assert not actual_file.exists(), f"File {relative_path} was not removed"

    assert not PixiRunner().has_dependency("django-allauth"), (
        "django-allauth dependency found after removal"
    )


def test_django_allauth_mfa_install_basic(temp_dir):
    """
    Test django-allauth MFA package installation with basic options (TOTP + recovery codes).
    """
    create_test_django_project(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "packages",
            "add",
            "django-allauth",
            "--provider",
            "account",
        ],
    )
    assert result.exit_code == 0, f"Account install failed: {result.output}"

    result = runner.invoke(
        app,
        [
            "packages",
            "add",
            "django-allauth",
            "--provider",
            "mfa",
        ],
    )

    assert result.exit_code == 0, f"MFA install failed: {result.output}"
    assert "Django Allauth installed." in result.output

    assert PixiRunner().has_dependency("django-allauth")

    mfa_settings_file = temp_dir / "settings" / "packages" / "django_allauth_mfa.py"
    assert mfa_settings_file.exists(), "MFA settings file not created"

    expected_mfa_settings_file = (
        DATA_DIR / "mfa" / "basic" / "settings" / "packages" / "django_allauth_mfa.py"
    )
    expected_content = expected_mfa_settings_file.read_text()
    actual_content = mfa_settings_file.read_text()
    assert actual_content == expected_content, "MFA settings content mismatch"

    mfa_index_template = (
        temp_dir / "authentication" / "templates" / "mfa" / "index.html"
    )
    assert mfa_index_template.exists(), "MFA index template not created"

    mfa_auth_template = (
        temp_dir / "authentication" / "templates" / "mfa" / "authenticate.html"
    )
    assert mfa_auth_template.exists(), "MFA authenticate template not created"


def test_django_allauth_mfa_install_with_webauthn(temp_dir):
    """
    Test django-allauth MFA package installation with WebAuthn enabled.
    """
    create_test_django_project(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "packages",
            "add",
            "django-allauth",
            "--provider",
            "account",
        ],
    )
    assert result.exit_code == 0, f"Account install failed: {result.output}"

    result = runner.invoke(
        app,
        [
            "packages",
            "add",
            "django-allauth",
            "--provider",
            "mfa",
        ],
    )

    assert result.exit_code == 0, f"MFA install failed: {result.output}"

    mfa_settings_file = temp_dir / "settings" / "packages" / "django_allauth_mfa.py"
    assert mfa_settings_file.exists(), "MFA settings file not created"

    settings_content = mfa_settings_file.read_text()
    assert "MFA_PASSKEY_LOGIN_ENABLED" not in settings_content
    assert "MFA_RECOVERY_CODE_COUNT = 10" in settings_content


def test_django_allauth_mfa_install_with_trust(temp_dir):
    """
    Test django-allauth MFA package installation with trust functionality enabled.
    """
    create_test_django_project(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "packages",
            "add",
            "django-allauth",
            "--provider",
            "account",
        ],
    )
    assert result.exit_code == 0, f"Account install failed: {result.output}"

    result = runner.invoke(
        app,
        [
            "packages",
            "add",
            "django-allauth",
            "--provider",
            "mfa",
        ],
    )

    assert result.exit_code == 0, f"MFA install failed: {result.output}"

    mfa_settings_file = temp_dir / "settings" / "packages" / "django_allauth_mfa.py"
    assert mfa_settings_file.exists(), "MFA settings file not created"

    settings_content = mfa_settings_file.read_text()
    assert "MFA_TRUST_ENABLED" not in settings_content, (
        "Trust should be disabled by default"
    )


def test_django_allauth_mfa_install_without_account(temp_dir):
    """
    Test django-allauth MFA installation. Account variant is a required dependency
    but MFA can still be installed in non-interactive mode.
    """
    create_test_django_project(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "packages",
            "add",
            "django-allauth",
            "--provider",
            "mfa",
        ],
    )

    assert result.exit_code == 0


def test_django_allauth_mfa_remove(temp_dir):
    """
    Test django-allauth MFA package removal.
    """
    create_test_django_project(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "packages",
            "add",
            "django-allauth",
            "--provider",
            "account",
        ],
    )
    assert result.exit_code == 0, f"Account install failed: {result.output}"

    result = runner.invoke(
        app,
        [
            "packages",
            "add",
            "django-allauth",
            "--provider",
            "mfa",
        ],
    )
    assert result.exit_code == 0, f"MFA install failed: {result.output}"

    result = runner.invoke(
        app,
        [
            "packages",
            "remove",
            "django-allauth",
            "--provider",
            "mfa",
        ],
    )

    assert result.exit_code == 0, f"MFA remove failed: {result.output}"
    assert "Django Allauth removed." in result.output

    mfa_settings_file = temp_dir / "settings" / "packages" / "django_allauth_mfa.py"
    assert not mfa_settings_file.exists(), "MFA settings file not removed"

    middleware_file = temp_dir / "authentication" / "middleware.py"
    assert not middleware_file.exists(), "MFA middleware file not removed"

    mfa_templates_dir = temp_dir / "authentication" / "templates" / "mfa"
    assert not mfa_templates_dir.exists(), "MFA templates directory not removed"

    data_mfa_dir = DATA_DIR / "mfa" / "basic"
    for expected_file in data_mfa_dir.rglob("*"):
        if expected_file.is_file():
            relative_path = expected_file.relative_to(data_mfa_dir)
            actual_file = temp_dir / relative_path
            assert not actual_file.exists(), f"File {relative_path} was not removed"

    assert PixiRunner().has_dependency("django-allauth"), (
        "django-allauth package should remain installed after MFA removal"
    )


def test_django_allauth_mfa_install_full_options(temp_dir):
    """
    Test django-allauth MFA package installation with all options enabled.
    """
    create_test_django_project(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "packages",
            "add",
            "django-allauth",
            "--provider",
            "account",
        ],
    )
    assert result.exit_code == 0, f"Account install failed: {result.output}"

    result = runner.invoke(
        app,
        [
            "packages",
            "add",
            "django-allauth",
            "--provider",
            "mfa",
        ],
    )

    assert result.exit_code == 0, f"MFA install failed: {result.output}"

    mfa_settings_file = temp_dir / "settings" / "packages" / "django_allauth_mfa.py"
    assert mfa_settings_file.exists(), "MFA settings file not created"

    settings_content = mfa_settings_file.read_text()

    assert "totp" in settings_content, "TOTP not enabled"

    assert "recovery_codes" in settings_content, "Recovery codes not enabled"
    assert "MFA_RECOVERY_CODE_COUNT = 10" in settings_content, (
        "Recovery code count not set"
    )

    assert "MFA_PASSKEY_LOGIN_ENABLED" not in settings_content, (
        "WebAuthn login not set to default"
    )

    assert "MFA_TRUST_ENABLED" not in settings_content, (
        "Trust should be disabled by default"
    )


def test_django_allauth_oidc_provider_install_without_account(temp_dir):
    """
    Test OIDC provider installation. Account variant is a required dependency
    but OIDC provider can still be installed in non-interactive mode.
    """
    create_test_django_project(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "packages",
            "add",
            "django-allauth",
            "--provider",
            "oidc_provider",
        ],
    )

    assert result.exit_code == 0


def test_django_allauth_oidc_provider_install_remove(temp_dir):
    """
    Test OIDC provider installation and removal with default settings.
    """
    create_test_django_project(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "packages",
            "add",
            "django-allauth",
            "--provider",
            "account",
        ],
    )
    assert result.exit_code == 0, f"Account install failed: {result.output}"

    result = runner.invoke(
        app,
        [
            "packages",
            "add",
            "django-allauth",
            "--provider",
            "oidc_provider",
        ],
    )

    assert result.exit_code == 0, f"OIDC provider install failed: {result.output}"
    assert "Django Allauth installed." in result.output

    settings_file = (
        temp_dir / "settings" / "packages" / "django_allauth_oidc_provider.py"
    )
    assert settings_file.exists(), "OIDC provider settings file not created"

    expected_settings_file = (
        DATA_DIR
        / "oidc_provider"
        / "settings"
        / "packages"
        / "django_allauth_oidc_provider.py"
    )
    expected_content = expected_settings_file.read_text()
    actual_content = settings_file.read_text()
    assert actual_content == expected_content, "OIDC provider settings content mismatch"

    urls_file = temp_dir / "urls" / "packages" / "django_allauth_oidc_provider.py"
    assert urls_file.exists(), "OIDC provider URLs file not created"

    expected_urls_file = (
        DATA_DIR
        / "oidc_provider"
        / "urls"
        / "packages"
        / "django_allauth_oidc_provider.py"
    )
    expected_urls_content = expected_urls_file.read_text()
    actual_urls_content = urls_file.read_text()
    assert actual_urls_content == expected_urls_content, (
        "OIDC provider URLs content mismatch"
    )

    secrets_dir = temp_dir / ".secrets"
    assert secrets_dir.exists(), ".secrets directory not created"
    secret_file = secrets_dir / "idp_oidc_private_key"
    assert secret_file.exists(), "idp_oidc_private_key secret file not found"

    secret_content = secret_file.read_text()
    assert "-----BEGIN PRIVATE KEY-----" in secret_content, (
        "Private key content not found in .secrets file"
    )
    assert "-----END PRIVATE KEY-----" in secret_content, (
        "Private key end marker not found in .secrets file"
    )

    test_templates_dir = DATA_DIR / "oidc_provider" / "authentication" / "templates"
    for expected_file in test_templates_dir.rglob("*"):
        if expected_file.is_file():
            relative_path = expected_file.relative_to(test_templates_dir)
            actual_file = temp_dir / "authentication" / "templates" / relative_path

            assert actual_file.exists(), f"Template file {relative_path} not created"

            expected_content = expected_file.read_text()
            actual_content = actual_file.read_text()
            assert actual_content == expected_content, (
                f"Template content mismatch in {relative_path}"
            )

    test_management_dir = DATA_DIR / "oidc_provider" / "authentication" / "management"
    for expected_file in test_management_dir.rglob("*"):
        if expected_file.is_file():
            relative_path = expected_file.relative_to(test_management_dir)
            actual_file = temp_dir / "authentication" / "management" / relative_path

            assert actual_file.exists(), (
                f"Management command file {relative_path} not created"
            )

            expected_content = expected_file.read_text()
            actual_content = actual_file.read_text()
            assert actual_content == expected_content, (
                f"Management command content mismatch in {relative_path}"
            )

    result = runner.invoke(
        app,
        [
            "packages",
            "remove",
            "django-allauth",
            "--provider",
            "oidc_provider",
        ],
    )

    assert result.exit_code == 0, f"OIDC provider remove failed: {result.output}"
    assert "Django Allauth removed." in result.output

    settings_file = (
        temp_dir / "settings" / "packages" / "django_allauth_oidc_provider.py"
    )
    assert not settings_file.exists(), "OIDC provider settings file not removed"

    urls_file = temp_dir / "urls" / "packages" / "django_allauth_oidc_provider.py"
    assert not urls_file.exists(), "OIDC provider URLs file not removed"

    assert not secret_file.exists(), "idp_oidc_private_key secret file was not removed"

    test_templates_dir = DATA_DIR / "oidc_provider" / "authentication" / "templates"
    for expected_file in test_templates_dir.rglob("*"):
        if expected_file.is_file():
            relative_path = expected_file.relative_to(test_templates_dir)
            actual_file = temp_dir / "authentication" / "templates" / relative_path
            assert not actual_file.exists(), (
                f"Template file {relative_path} was not removed"
            )

    test_management_dir = DATA_DIR / "oidc_provider" / "authentication" / "management"
    for expected_file in test_management_dir.rglob("*"):
        if expected_file.is_file():
            relative_path = expected_file.relative_to(test_management_dir)
            actual_file = temp_dir / "authentication" / "management" / relative_path
            assert not actual_file.exists(), (
                f"Management command file {relative_path} was not removed"
            )

    assert PixiRunner().has_dependency("django-allauth"), (
        "django-allauth package should remain installed after OIDC provider removal"
    )
