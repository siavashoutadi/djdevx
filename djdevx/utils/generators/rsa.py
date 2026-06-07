"""RSA key generation utilities."""

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def generate_rsa_private_key(key_size: int = 2048) -> str:
    """
    Generate an RSA private key in PKCS8 PEM format.

    Args:
        key_size: RSA key size in bits. Defaults to 2048.

    Returns:
        PEM-encoded private key as a string.
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend(),
    )
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")
