"""Random password generation utilities."""

import secrets
import string


def generate_random_password(length: int = 32) -> str:
    """
    Generate a cryptographically random password.

    Uses letters and digits only to avoid shell-escaping issues when the
    password is embedded in scripts or YAML files.

    Args:
        length: Length of the generated password. Defaults to 32.

    Returns:
        A random password string.
    """
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))
