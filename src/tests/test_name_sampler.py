"""Tests for the BrazilianNameSampler class."""
import pytest
from src.name_sampler import BrazilianNameSampler
from src.time_period import TimePeriod

def test_name_sampler_initialization(test_data_path):
    """Test that sampler initializes correctly with valid data."""
    sampler = BrazilianNameSampler(test_data_path)
    assert sampler.name_data is not None
    assert sampler.surname_data is not None

def test_name_sampler_invalid_path():
    """Test that sampler raises error with invalid file path."""
    with pytest.raises(FileNotFoundError):
        BrazilianNameSampler('invalid_path.json')

def test_random_name_generation(test_data):
    """Test basic name generation."""
    sampler = BrazilianNameSampler(test_data)
    name = sampler.get_random_name()
    assert isinstance(name, str)
    assert len(name) > 0

def test_random_name_with_period(test_data):
    """Test name generation for specific time period."""
    sampler = BrazilianNameSampler(test_data)
    name = sampler.get_random_name(time_period=TimePeriod.UNTIL_2010)
    assert isinstance(name, str)
    assert len(name) > 0

def test_random_surname(test_data):
    """Test surname generation."""
    sampler = BrazilianNameSampler(test_data)
    surname = sampler.get_random_surname()
    assert isinstance(surname, str)
    assert len(surname) > 0
    assert ' ' in surname  # Should have two surnames by default

def test_single_surname(test_data):
    """Test single surname generation."""
    sampler = BrazilianNameSampler(test_data)
    surname = sampler.get_random_surname(with_only_one_surname=True)
    assert isinstance(surname, str)
    assert len(surname) > 0
    
def test_top_40_surname(test_data):
    """Test top 40 surname generation."""
    sampler = BrazilianNameSampler(test_data)
    surname = sampler.get_random_surname(top_40=True)
    assert isinstance(surname, str)
    assert len(surname) > 0

def test_raw_name_format(test_data):
    """Test raw name format."""
    sampler = BrazilianNameSampler(test_data)
    name = sampler.get_random_name(raw=True)
    assert name.isupper()
