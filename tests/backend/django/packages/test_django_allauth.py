from pathlib import Path
import os
from typer.testing import CliRunner
from djdevx.main import app
from djdevx.utils.django.project_manager import DjangoProjectManager
from tests.test_helpers import create_test_django_backend

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "django_allauth"


def test_django_allauth_account_install_and_remove(temp_dir):
    """
    Test django-allauth account package installation and removal.
    """

    backend_dir = create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

    # Test install with specific values for templating
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-allauth",
            "account",
            "install",
            "--email-subject-prefix",
            "[Test Site] ",
            "--enable-login-by-code",
            "--is-profanity-for-username-enabled",
            "--account-url-prefix",
            "auth",
        ],
    )

    assert result.exit_code == 0, f"Install failed: {result.output}"

    # Check settings file
    settings_file = backend_dir / "settings" / "packages" / "django_allauth_account.py"
    assert settings_file.exists(), "Settings file not created"

    expected_settings_file = (
        DATA_DIR / "account" / "settings" / "packages" / "django_allauth_account.py"
    )
    expected_content = expected_settings_file.read_text()
    actual_content = settings_file.read_text()
    assert actual_content == expected_content, "Settings content mismatch"

    # Check URLs file
    urls_file = backend_dir / "urls" / "packages" / "django_allauth_account.py"
    assert urls_file.exists(), "URLs file not created"

    expected_urls_file = (
        DATA_DIR / "account" / "urls" / "packages" / "django_allauth_account.py"
    )
    expected_urls_content = expected_urls_file.read_text()
    actual_urls_content = urls_file.read_text()
    assert actual_urls_content == expected_urls_content, "URLs content mismatch"

    # Check authentication app files
    auth_app_file = backend_dir / "authentication" / "__init__.py"
    assert auth_app_file.exists(), "Authentication app __init__.py not created"

    auth_apps_file = backend_dir / "authentication" / "apps.py"
    assert auth_apps_file.exists(), "Authentication apps.py not created"

    # Check dependencies
    assert DjangoProjectManager().has_dependency("django-allauth"), (
        "django-allauth dependency not found after installation"
    )
    assert DjangoProjectManager().has_dependency("better-profanity"), (
        "better-profanity dependency not found after installation"
    )

    data_account_dir = DATA_DIR / "account"
    for expected_file in data_account_dir.rglob("*"):
        if expected_file.is_file():
            relative_path = expected_file.relative_to(data_account_dir)
            actual_file = backend_dir / relative_path

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
            "backend",
            "django",
            "packages",
            "django-allauth",
            "account",
            "remove",
        ],
    )

    assert result.exit_code == 0, f"Remove failed: {result.output}"

    # Verify files are removed
    assert not settings_file.exists(), "Settings file not removed"
    assert not urls_file.exists(), "URLs file not removed"
    assert not auth_app_file.parent.exists(), "Authentication directory not removed"

    # Verify all account files are removed
    data_account_dir = DATA_DIR / "account"
    for expected_file in data_account_dir.rglob("*"):
        if expected_file.is_file():
            relative_path = expected_file.relative_to(data_account_dir)
            actual_file = backend_dir / relative_path
            assert not actual_file.exists(), f"File {relative_path} was not removed"

    # Check dependencies are removed
    assert not DjangoProjectManager().has_dependency("django-allauth"), (
        "django-allauth dependency found after removal"
    )
    assert not DjangoProjectManager().has_dependency("better-profanity"), (
        "better-profanity dependency found after removal"
    )


def test_django_allauth_mfa_install_basic(temp_dir):
    """
    Test django-allauth MFA package installation with basic options (TOTP + recovery codes).
    """
    backend_dir = create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

    # First install account functionality
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-allauth",
            "account",
            "install",
            "--email-subject-prefix",
            "[Test Site] ",
            "--enable-login-by-code",
            "--is-profanity-for-username-enabled",
            "--account-url-prefix",
            "auth",
        ],
    )
    assert result.exit_code == 0, f"Account install failed: {result.output}"

    # Test MFA install with basic options
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-allauth",
            "mfa",
            "install",
            "--enable-totp",
            "--enable-recovery-codes",
            "--no-enable-webauthn",
            "--no-enable-trust",
            "--totp-issuer",
            "Test App",
            "--totp-period",
            "30",
            "--totp-digits",
            "6",
            "--totp-tolerance",
            "0",
            "--recovery-code-count",
            "10",
            "--recovery-code-digits",
            "8",
            "--no-passkey-login",
            "--no-passkey-signup",
            "--no-webauthn-allow-insecure",
            "--trust-cookie-age-days",
            "14",
        ],
    )

    assert result.exit_code == 0, f"MFA install failed: {result.output}"
    assert (
        "django-allauth with MFA functionality is installed successfully"
        in result.output
    )

    # Check if package is upgraded to include MFA
    assert DjangoProjectManager().has_dependency("django-allauth")

    # Check if MFA settings file is created
    mfa_settings_file = backend_dir / "settings" / "packages" / "django_allauth_mfa.py"
    assert mfa_settings_file.exists(), "MFA settings file not created"

    # Verify settings content for basic install
    expected_mfa_settings_file = (
        DATA_DIR / "mfa" / "basic" / "settings" / "packages" / "django_allauth_mfa.py"
    )
    expected_content = expected_mfa_settings_file.read_text()
    actual_content = mfa_settings_file.read_text()
    assert actual_content == expected_content, "MFA settings content mismatch"

    # Check if authentication templates are created
    mfa_index_template = (
        backend_dir / "authentication" / "templates" / "mfa" / "index.html"
    )
    assert mfa_index_template.exists(), "MFA index template not created"

    mfa_auth_template = (
        backend_dir / "authentication" / "templates" / "mfa" / "authenticate.html"
    )
    assert mfa_auth_template.exists(), "MFA authenticate template not created"


def test_django_allauth_mfa_install_with_webauthn(temp_dir):
    """
    Test django-allauth MFA package installation with WebAuthn enabled.
    """
    backend_dir = create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

    # First install account functionality
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-allauth",
            "account",
            "install",
            "--email-subject-prefix",
            "[Test Site] ",
            "--enable-login-by-code",
            "--no-is-profanity-for-username-enabled",
            "--account-url-prefix",
            "auth",
        ],
    )
    assert result.exit_code == 0, f"Account install failed: {result.output}"

    # Test MFA install with WebAuthn enabled
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-allauth",
            "mfa",
            "install",
            "--enable-totp",
            "--enable-recovery-codes",
            "--enable-webauthn",
            "--no-enable-trust",
            "--totp-issuer",
            "Test App",
            "--totp-period",
            "30",
            "--totp-digits",
            "6",
            "--totp-tolerance",
            "0",
            "--recovery-code-count",
            "12",
            "--recovery-code-digits",
            "8",
            "--passkey-login",
            "--passkey-signup",
            "--no-webauthn-allow-insecure",
            "--trust-cookie-age-days",
            "14",
        ],
    )

    assert result.exit_code == 0, f"MFA install failed: {result.output}"

    # Check if MFA settings file is created with WebAuthn
    mfa_settings_file = backend_dir / "settings" / "packages" / "django_allauth_mfa.py"
    assert mfa_settings_file.exists(), "MFA settings file not created"

    # Verify WebAuthn is included in settings
    settings_content = mfa_settings_file.read_text()
    assert "webauthn" in settings_content, "WebAuthn not enabled in settings"
    assert "MFA_PASSKEY_LOGIN_ENABLED = True" in settings_content, (
        "WebAuthn login not enabled"
    )
    assert "MFA_RECOVERY_CODE_COUNT = 12" in settings_content, (
        "Recovery code count not set"
    )


def test_django_allauth_mfa_install_with_trust(temp_dir):
    """
    Test django-allauth MFA package installation with trust functionality enabled.
    """
    backend_dir = create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

    # First install account functionality
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-allauth",
            "account",
            "install",
            "--email-subject-prefix",
            "[Test Site] ",
            "--enable-login-by-code",
            "--no-is-profanity-for-username-enabled",
            "--account-url-prefix",
            "auth",
        ],
    )
    assert result.exit_code == 0, f"Account install failed: {result.output}"

    # Test MFA install with trust enabled
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-allauth",
            "mfa",
            "install",
            "--enable-totp",
            "--enable-recovery-codes",
            "--no-enable-webauthn",
            "--enable-trust",
            "--totp-issuer",
            "Test App",
            "--totp-period",
            "30",
            "--totp-digits",
            "6",
            "--totp-tolerance",
            "0",
            "--recovery-code-count",
            "10",
            "--recovery-code-digits",
            "8",
            "--no-passkey-login",
            "--no-passkey-signup",
            "--no-webauthn-allow-insecure",
            "--trust-cookie-age-days",
            "30",
        ],
    )

    assert result.exit_code == 0, f"MFA install failed: {result.output}"

    # Check if MFA settings file is created with trust
    mfa_settings_file = backend_dir / "settings" / "packages" / "django_allauth_mfa.py"
    assert mfa_settings_file.exists(), "MFA settings file not created"

    # Verify trust functionality is included in settings
    settings_content = mfa_settings_file.read_text()
    assert "MFA_TRUST_ENABLED = True" in settings_content, (
        "Trust functionality not enabled"
    )
    assert "MFA_TRUST_COOKIE_AGE = 2592000" in settings_content, (
        "Trust cookie age not set (30 days)"
    )


def test_django_allauth_mfa_install_without_account(temp_dir):
    """
    Test django-allauth MFA installation fails when account is not installed first.
    """
    create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

    # Try to install MFA without account functionality
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-allauth",
            "mfa",
            "install",
            "--enable-totp",
            "--enable-recovery-codes",
            "--no-enable-webauthn",
            "--no-enable-trust",
            "--totp-issuer",
            "Test App",
            "--totp-period",
            "30",
            "--totp-digits",
            "6",
            "--totp-tolerance",
            "0",
            "--recovery-code-count",
            "10",
            "--recovery-code-digits",
            "8",
            "--no-passkey-login",
            "--no-passkey-signup",
            "--no-webauthn-allow-insecure",
            "--trust-cookie-age-days",
            "14",
        ],
    )

    assert result.exit_code == 1, "MFA install should fail without account"
    assert "django-allauth" in result.output and "not installed" in result.output


def test_django_allauth_mfa_remove(temp_dir):
    """
    Test django-allauth MFA package removal.
    """
    backend_dir = create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

    # First install account functionality
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-allauth",
            "account",
            "install",
            "--email-subject-prefix",
            "[Test Site] ",
            "--enable-login-by-code",
            "--no-is-profanity-for-username-enabled",
            "--account-url-prefix",
            "auth",
        ],
    )
    assert result.exit_code == 0, f"Account install failed: {result.output}"

    # Install MFA
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-allauth",
            "mfa",
            "install",
            "--enable-totp",
            "--enable-recovery-codes",
            "--no-enable-webauthn",
            "--no-enable-trust",
            "--totp-issuer",
            "Test App",
            "--totp-period",
            "30",
            "--totp-digits",
            "6",
            "--totp-tolerance",
            "0",
            "--recovery-code-count",
            "10",
            "--recovery-code-digits",
            "8",
            "--no-passkey-login",
            "--no-passkey-signup",
            "--no-webauthn-allow-insecure",
            "--trust-cookie-age-days",
            "14",
        ],
    )
    assert result.exit_code == 0, f"MFA install failed: {result.output}"

    # Test MFA removal
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-allauth",
            "mfa",
            "remove",
        ],
    )

    assert result.exit_code == 0, f"MFA remove failed: {result.output}"
    assert "django-allauth MFA configuration is removed successfully" in result.output

    mfa_settings_file = backend_dir / "settings" / "packages" / "django_allauth_mfa.py"
    assert not mfa_settings_file.exists(), "MFA settings file not removed"

    middleware_file = backend_dir / "authentication" / "middleware.py"
    assert not middleware_file.exists(), "MFA middleware file not removed"

    mfa_templates_dir = backend_dir / "authentication" / "templates" / "mfa"
    assert not mfa_templates_dir.exists(), "MFA templates directory not removed"

    # Verify all MFA files are removed
    data_mfa_dir = DATA_DIR / "mfa" / "basic"
    for expected_file in data_mfa_dir.rglob("*"):
        if expected_file.is_file():
            relative_path = expected_file.relative_to(data_mfa_dir)
            actual_file = backend_dir / relative_path
            assert not actual_file.exists(), f"File {relative_path} was not removed"

    # Verify django-allauth package is still installed (only MFA config removed)
    assert DjangoProjectManager().has_dependency("django-allauth"), (
        "django-allauth package should remain installed after MFA removal"
    )


def test_django_allauth_mfa_install_full_options(temp_dir):
    """
    Test django-allauth MFA package installation with all options enabled.
    """
    backend_dir = create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

    # First install account functionality
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-allauth",
            "account",
            "install",
            "--email-subject-prefix",
            "[Test Site] ",
            "--enable-login-by-code",
            "--no-is-profanity-for-username-enabled",
            "--account-url-prefix",
            "auth",
        ],
    )
    assert result.exit_code == 0, f"Account install failed: {result.output}"

    # Test MFA install with all features
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-allauth",
            "mfa",
            "install",
            "--enable-totp",
            "--enable-recovery-codes",
            "--enable-webauthn",
            "--enable-trust",
            "--totp-issuer",
            "Full Featured App",
            "--totp-period",
            "30",
            "--totp-digits",
            "6",
            "--totp-tolerance",
            "0",
            "--recovery-code-count",
            "15",
            "--recovery-code-digits",
            "8",
            "--passkey-login",
            "--passkey-signup",
            "--no-webauthn-allow-insecure",
            "--trust-cookie-age-days",
            "7",
        ],
    )

    assert result.exit_code == 0, f"MFA install failed: {result.output}"

    # Check if MFA settings file is created with all options
    mfa_settings_file = backend_dir / "settings" / "packages" / "django_allauth_mfa.py"
    assert mfa_settings_file.exists(), "MFA settings file not created"

    # Verify all features are included in settings
    settings_content = mfa_settings_file.read_text()

    # Check TOTP settings
    assert "totp" in settings_content, "TOTP not enabled"
    assert 'MFA_TOTP_ISSUER = "Full Featured App"' in settings_content, (
        "TOTP issuer not set"
    )

    # Check recovery codes settings
    assert "recovery_codes" in settings_content, "Recovery codes not enabled"
    assert "MFA_RECOVERY_CODE_COUNT = 15" in settings_content, (
        "Recovery code count not set"
    )

    # Check WebAuthn settings
    assert "webauthn" in settings_content, "WebAuthn not enabled"
    assert "MFA_PASSKEY_LOGIN_ENABLED = True" in settings_content, (
        "WebAuthn login not enabled"
    )

    # Check trust settings
    assert "MFA_TRUST_ENABLED = True" in settings_content, (
        "Trust functionality not enabled"
    )
    assert "MFA_TRUST_COOKIE_AGE = 604800" in settings_content, (
        "Trust cookie age not set (7 days)"
    )


def test_django_allauth_oidc_provider_install_without_account(temp_dir):
    """
    Test OIDC provider installation fails if account is not installed first.
    """
    create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-allauth",
            "oidc-provider",
            "install",
        ],
    )

    assert result.exit_code == 1, "OIDC provider install should fail without account"
    assert "account functionality is not configured" in result.output


def test_django_allauth_oidc_provider_install_remove(temp_dir):
    """
    Test OIDC provider installation and removal with default settings.
    """
    backend_dir = create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-allauth",
            "account",
            "install",
            "--email-subject-prefix",
            "[Test Site] ",
            "--enable-login-by-code",
            "--no-is-profanity-for-username-enabled",
            "--account-url-prefix",
            "auth",
        ],
    )
    assert result.exit_code == 0, f"Account install failed: {result.output}"

    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-allauth",
            "oidc-provider",
            "install",
        ],
    )

    assert result.exit_code == 0, f"OIDC provider install failed: {result.output}"
    assert "django-allauth OIDC provider is installed successfully" in result.output

    # Check settings file
    settings_file = (
        backend_dir / "settings" / "packages" / "django_allauth_oidc_provider.py"
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

    # Check URLs file
    urls_file = backend_dir / "urls" / "packages" / "django_allauth_oidc_provider.py"
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

    # Check that private key was added to .env file
    env_file = backend_dir.parent / ".devcontainer" / ".env" / "devcontainer"
    assert env_file.exists(), f".env devcontainer file not found at {env_file}"

    env_content = env_file.read_text()
    assert "IDP_OIDC_PRIVATE_KEY=" in env_content, (
        "IDP_OIDC_PRIVATE_KEY not added to .env file"
    )
    assert "-----BEGIN PRIVATE KEY-----" in env_content, (
        "Private key content not found in .env file"
    )
    assert "-----END PRIVATE KEY-----" in env_content, (
        "Private key end marker not found in .env file"
    )

    # Check OIDC provider templates are created
    test_templates_dir = DATA_DIR / "oidc_provider" / "authentication" / "templates"
    for expected_file in test_templates_dir.rglob("*"):
        if expected_file.is_file():
            relative_path = expected_file.relative_to(test_templates_dir)
            actual_file = backend_dir / "authentication" / "templates" / relative_path

            assert actual_file.exists(), f"Template file {relative_path} not created"

            expected_content = expected_file.read_text()
            actual_content = actual_file.read_text()
            assert actual_content == expected_content, (
                f"Template content mismatch in {relative_path}"
            )

    # Check OIDC provider management commands are created
    test_management_dir = DATA_DIR / "oidc_provider" / "authentication" / "management"
    for expected_file in test_management_dir.rglob("*"):
        if expected_file.is_file():
            relative_path = expected_file.relative_to(test_management_dir)
            actual_file = backend_dir / "authentication" / "management" / relative_path

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
            "backend",
            "django",
            "packages",
            "django-allauth",
            "oidc-provider",
            "remove",
        ],
    )

    assert result.exit_code == 0, f"OIDC provider remove failed: {result.output}"
    assert (
        "django-allauth OIDC provider configuration is removed successfully"
        in result.output
    )

    settings_file = (
        backend_dir / "settings" / "packages" / "django_allauth_oidc_provider.py"
    )
    assert not settings_file.exists(), "OIDC provider settings file not removed"

    urls_file = backend_dir / "urls" / "packages" / "django_allauth_oidc_provider.py"
    assert not urls_file.exists(), "OIDC provider URLs file not removed"

    # Check that private key was removed from .env file
    env_content = env_file.read_text()
    assert "IDP_OIDC_PRIVATE_KEY=" not in env_content, (
        "IDP_OIDC_PRIVATE_KEY not removed from .env file"
    )
    assert "-----BEGIN PRIVATE KEY-----" not in env_content, (
        "Private key content still in .env file"
    )
    assert "-----END PRIVATE KEY-----" not in env_content, (
        "Private key end marker still in .env file"
    )

    # Verify OIDC provider templates are removed
    test_templates_dir = DATA_DIR / "oidc_provider" / "authentication" / "templates"
    for expected_file in test_templates_dir.rglob("*"):
        if expected_file.is_file():
            relative_path = expected_file.relative_to(test_templates_dir)
            actual_file = backend_dir / "authentication" / "templates" / relative_path
            assert not actual_file.exists(), (
                f"Template file {relative_path} was not removed"
            )

    # Verify OIDC provider management commands are removed
    test_management_dir = DATA_DIR / "oidc_provider" / "authentication" / "management"
    for expected_file in test_management_dir.rglob("*"):
        if expected_file.is_file():
            relative_path = expected_file.relative_to(test_management_dir)
            actual_file = backend_dir / "authentication" / "management" / relative_path
            assert not actual_file.exists(), (
                f"Management command file {relative_path} was not removed"
            )

    assert DjangoProjectManager().has_dependency("django-allauth"), (
        "django-allauth package should remain installed after OIDC provider removal"
    )
