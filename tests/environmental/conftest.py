"""Test configuration for environmental module."""

import pytest
from pathlib import Path
from datetime import datetime

@pytest.fixture(scope="session")
def test_data_dir(tmp_path_factory) -> Path:
    """Create and return a temporary directory for test data."""
    return tmp_path_factory.mktemp("environmental_test_data")
