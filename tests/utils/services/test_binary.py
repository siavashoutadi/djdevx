"""Tests for the pinned binary release URLs and checksum verification."""

import hashlib
import io
import tarfile
from unittest.mock import MagicMock, patch

import pytest

from djdevx.utils.services import binary


def _tarball_bytes(payload_name: str = "otelcol-contrib") -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        data = b"#!/bin/sh\necho hi\n"
        info = tarfile.TarInfo(payload_name)
        info.size = len(data)
        info.mode = 0o755
        tf.addfile(info, io.BytesIO(data))
    return buf.getvalue()


def _serve(data: bytes):
    resp = MagicMock()
    resp.read.return_value = data
    resp.__enter__.return_value = resp
    return patch.object(binary.urllib.request, "urlopen", return_value=resp)


def test_otelcol_release_url_is_pinned(monkeypatch):
    monkeypatch.setattr(binary, "platform_key", lambda: "linux-amd64")
    url = binary.otelcol_contrib_release_url()
    assert url == (
        "https://github.com/open-telemetry/opentelemetry-collector-releases"
        "/releases/download/v0.159.0/otelcol-contrib_0.159.0_linux_amd64.tar.gz"
    )


def test_openobserve_release_url_is_pinned(monkeypatch):
    monkeypatch.setattr(binary, "platform_key", lambda: "windows-amd64")
    url = binary.openobserve_release_url()
    assert url.endswith("openobserve-v0.92.2-windows-amd64.zip")
    assert url.startswith("https://downloads.openobserve.ai/releases/openobserve/")


def test_unknown_platform_refuses_to_resolve(monkeypatch):
    monkeypatch.setattr(binary, "platform_key", lambda: "plan9-riscv")
    with pytest.raises(RuntimeError, match="refusing to download"):
        binary.otelcol_contrib_release_url()
    with pytest.raises(RuntimeError, match="refusing to download"):
        binary.openobserve_release_url()
    with pytest.raises(RuntimeError, match="refusing to download"):
        binary.otelcol_contrib_sha256()


def test_download_and_extract_verifies_matching_sha256(tmp_path):
    data = _tarball_bytes()
    digest = hashlib.sha256(data).hexdigest()
    with _serve(data):
        result = binary.download_and_extract(
            "https://example.invalid/otelcol.tar.gz",
            tmp_path,
            binary_glob="otelcol*",
            expected_sha256=digest,
        )
    assert result is not None
    assert result.name == "otelcol-contrib"
    assert result.stat().st_mode & 0o111  # executable bit set


def test_download_and_extract_rejects_bad_sha256_before_extraction(tmp_path):
    data = _tarball_bytes()
    with _serve(data), pytest.raises(RuntimeError, match="SHA256 mismatch"):
        binary.download_and_extract(
            "https://example.invalid/otelcol.tar.gz",
            tmp_path,
            binary_glob="otelcol*",
            expected_sha256="0" * 64,
        )
    # Nothing extracted, no archive left behind.
    assert list(tmp_path.iterdir()) == []


def test_download_and_extract_without_expected_hash_still_works(tmp_path):
    data = _tarball_bytes("openobserve")
    with _serve(data):
        result = binary.download_and_extract(
            "https://example.invalid/oo.tar.gz",
            tmp_path,
            binary_glob="openobserve*",
        )
    assert result is not None and result.name == "openobserve"
