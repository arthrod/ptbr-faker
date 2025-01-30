from pathlib import Path

import pytest
from sampler_ptbr import BrazilianLocationSampler, BrazilianNameSampler, TimePeriod, app
from typer.testing import CliRunner

runner = CliRunner()

# Test data path - adjust this to your actual test data file path
TEST_JSON_PATH = 'population_data_2024_with_postalcodes.json'


def test_json_file_exists():
    """Test if the JSON data file exists"""
    assert Path(TEST_JSON_PATH).exists(), f'Test data file {TEST_JSON_PATH} not found'


def test_basic_sample():
    """Test basic sample generation"""
    result = runner.invoke(app, ['--json-path', TEST_JSON_PATH])
    assert result.exit_code == 0
    assert len(result.stdout) > 0


def test_multiple_samples():
    """Test generating multiple samples"""
    result = runner.invoke(app, ['--qty', '5', '--json-path', TEST_JSON_PATH])
    assert result.exit_code == 0
    # Count the number of lines in the output (excluding table borders)
    assert result.stdout.count('\n') >= 5


def test_city_only():
    """Test city-only output"""
    result = runner.invoke(app, ['--city-only', '--json-path', TEST_JSON_PATH])
    assert result.exit_code == 0
    # Verify no commas in output (since it's just city names)
    assert ',' not in result.stdout


def test_state_abbreviation():
    """Test state abbreviation output"""
    result = runner.invoke(app, ['--state-abbr-only', '--json-path', TEST_JSON_PATH])
    assert result.exit_code == 0
    # Check if output contains 2-letter state code
    output_lines = result.stdout.strip().split('\n')
    assert any(len(line.strip()) == 2 for line in output_lines)


def test_state_full_name():
    """Test full state name output"""
    result = runner.invoke(app, ['--state-full-only', '--json-path', TEST_JSON_PATH])
    assert result.exit_code == 0
    assert len(result.stdout) > 0


def test_cep_format():
    """Test CEP format with and without dash"""
    # Test with dash
    result = runner.invoke(app, ['--only-cep', '--json-path', TEST_JSON_PATH])
    assert result.exit_code == 0
    assert '-' in result.stdout

    # Test without dash
    result = runner.invoke(app, ['--only-cep', '--cep-without-dash', '--json-path', TEST_JSON_PATH])
    assert result.exit_code == 0
    assert '-' not in result.stdout


def test_time_periods():
    """Test different time periods for name sampling"""
    for period in TimePeriod:
        result = runner.invoke(app, ['--time-period', period.value, '--return-only-name', '--json-path', TEST_JSON_PATH])
        assert result.exit_code == 0
        assert len(result.stdout) > 0


def test_name_raw_format():
    """Test raw name format (all caps)"""
    result = runner.invoke(app, ['--return-only-name', '--name-raw', '--json-path', TEST_JSON_PATH])
    assert result.exit_code == 0
    # Check if output contains uppercase letters
    output_text = result.stdout.strip()
    assert any(c.isupper() for c in output_text)


def test_location_sampler_initialization():
    """Test BrazilianLocationSampler initialization"""
    sampler = BrazilianLocationSampler(TEST_JSON_PATH)
    assert sampler is not None
    assert hasattr(sampler, 'data')
    assert hasattr(sampler, 'state_weights')
    assert hasattr(sampler, 'city_weights_by_state')


def test_name_sampler_initialization():
    """Test BrazilianNameSampler initialization"""
    sampler = BrazilianNameSampler(TEST_JSON_PATH)
    assert sampler is not None
    assert hasattr(sampler, 'name_data')


def test_cep_validation():
    """Test CEP format validation"""
    sampler = BrazilianLocationSampler(TEST_JSON_PATH)
    city, _ = sampler.get_city()
    cep = sampler._get_random_cep_for_city(city)

    # Test with dash
    formatted_cep = sampler._format_cep(cep, True)
    assert len(formatted_cep) == 9
    assert '-' in formatted_cep

    # Test without dash
    formatted_cep = sampler._format_cep(cep, False)
    assert len(formatted_cep) == 8
    assert '-' not in formatted_cep


def test_error_handling():
    """Test error handling with invalid inputs"""
    # Test with non-existent JSON file
    result = runner.invoke(app, ['--json-path', 'nonexistent.json'])
    assert result.exit_code == 1

    # Test with invalid time period
    result = runner.invoke(app, ['--time-period', 'invalid_period'])
    assert result.exit_code == 2


def test_combined_options():
    """Test combinations of different options"""
    result = runner.invoke(app, ['--qty', '3', '--cep-without-dash', '--time-period', 'ate2010', '--json-path', TEST_JSON_PATH])
    assert result.exit_code == 0
    assert len(result.stdout) > 0


if __name__ == '__main__':
    pytest.main(['-v', __file__])
