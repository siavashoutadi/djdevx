# conftest.py
import os
import shutil
import stat
from pathlib import Path

import pytest


def _force_remove(func, path, _exc):
    try:
        os.chmod(path, stat.S_IRWXU)
    except OSError:
        pass
    func(path)


def _remove_tree(path: Path) -> None:
    if not path.exists():
        return
    try:
        shutil.rmtree(path, onexc=_force_remove)
    except OSError:
        shutil.rmtree(path, ignore_errors=True)


@pytest.fixture
def temp_dir(tmp_path):
    """
    Per-test temporary directory, as a pathlib.Path.
    Each test gets a unique folder under pytest's temp root.

    The directory is removed at teardown so project-scaffolding tests (which
    create large pixi environments) do not exhaust the CI disk.
    """
    original_cwd = Path.cwd()
    yield tmp_path
    try:
        os.chdir(original_cwd)
    finally:
        _remove_tree(tmp_path)
