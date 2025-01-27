"""Test configuration and fixtures."""
import json
from pathlib import Path
import pytest

@pytest.fixture
def test_data_path() -> Path:
    """Return path to test data file."""
    return Path('data/population_data_2024_with_postalcodes_updated.json')

@pytest.fixture
def test_data(test_data_path) -> dict:
    """Load test data from JSON file."""
    with test_data_path.open(encoding='utf-8') as f:
        return json.load(f)
