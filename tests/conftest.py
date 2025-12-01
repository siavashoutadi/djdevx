# conftest.py
import pytest


@pytest.fixture
def temp_dir(tmp_path):
    """
    Per-test temporary directory, as a pathlib.Path.
    Each test gets a unique folder under pytest's temp root.
    """
    return tmp_path
