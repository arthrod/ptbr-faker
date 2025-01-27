"""Test configuration and fixtures."""
import json
from pathlib import Path
import pytest
from typing import Dict, Any

@pytest.fixture
def test_data_path() -> Path:
    """Return path to test data file."""
    return Path('data/population_data_2024_with_postalcodes_updated.json')

@pytest.fixture
def test_data(test_data_path) -> Dict[str, Any]:
    """Load test data from JSON file."""
    with test_data_path.open(encoding='utf-8') as f:
        return json.load(f)

@pytest.fixture
def minimal_test_data() -> Dict[str, Any]:
    """Return minimal valid test data structure."""
    return {
        "common_names_percentage": {
            period.value: {"names": {"TEST": {"percentage": 1.0}}, "total": 1}
            for period in TimePeriod
        },
        "surnames": {
            "TEST": {"percentage": 1.0},
            "top_40": {"TEST": {"percentage": 1.0}}
        }
    }
