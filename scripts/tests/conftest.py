"""Pytest configuration for repository scripts and workflow tests."""

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "unit: unit test for scripts and workflow assets")
