import json
import random
from enum import Enum
from pathlib import Path

from src.time_period import TimePeriod


class BrazilianNameSampler:
    def __init__(self, json_file_path: str | Path | dict) -> None:
        """
        Initialize the name sampler with population data.
        Now accepts either a file path or pre-loaded data.

        Args:
            json_file_path: Path to JSON file or pre-loaded data dictionary
        """
        if isinstance(json_file_path, str | Path):
            with Path(json_file_path).open(encoding='utf-8') as file:
                data = json.load(file)
        else:
            data = json_file_path

        if 'common_names_percentage' not in data:
            raise ValueError("Missing 'common_names_percentage' data")

        self.name_data = data['common_names_percentage']
        self._validate_data()

    def _validate_data(self) -> None:
        """
        Validate the name data structure has all required time periods and correct format.

        Raises:
            ValueError: If any required data structure is missing or invalid
        """
        for period in TimePeriod:
            if period.value not in self.name_data:
                raise ValueError(f'Missing data for time period: {period.value}')

            period_data = self.name_data[period.value]
            if not {'names', 'total'}.issubset(period_data.keys()):
                raise ValueError(f"Invalid data structure for period {period.value}. Must contain 'names' and 'total'")

    def get_random_name(self, time_period: TimePeriod = TimePeriod.UNTIL_2010, raw: bool = False) -> str:
        """
        Get a random name from the specified time period.

        Args:
            time_period: Historical period to sample from
            raw: If True, returns name in original format, if False, converts to Title Case
        """
        period_data = self.name_data[time_period.value]
        names_data = period_data['names']

        names = []
        weights = []
        for name, info in names_data.items():
            names.append(name)
            weights.append(info['percentage'])

        name = random.choices(names, weights=weights, k=1)[0]
        return name if raw else name.title()
import json
import random
from enum import Enum
from pathlib import Path

from src.time_period import TimePeriod


class BrazilianNameSampler:
    def __init__(self, json_file_path: str | Path | dict):
        """
        Initialize the name sampler with population data.
        Now accepts either a file path or pre-loaded data.

        Args:
            json_file_path: Path to JSON file or pre-loaded data dictionary
        """
        if isinstance(json_file_path, str | Path):
            with Path(json_file_path).open(encoding='utf-8') as file:
                data = json.load(file)
        else:
            data = json_file_path

        if 'common_names_percentage' not in data:
            raise ValueError("Missing 'common_names_percentage' data")

        self.name_data = data['common_names_percentage']
        self._validate_data()

    def _validate_data(self) -> None:
        """
        Validate the name data structure has all required time periods and correct format.

        Raises:
            ValueError: If any required data structure is missing or invalid
        """
        for period in TimePeriod:
            if period.value not in self.name_data:
                raise ValueError(f'Missing data for time period: {period.value}')

            period_data = self.name_data[period.value]
            if not {'names', 'total'}.issubset(period_data.keys()):
                raise ValueError(f"Invalid data structure for period {period.value}. Must contain 'names' and 'total'")

    def get_random_name(self, time_period: TimePeriod = TimePeriod.UNTIL_2010, raw: bool = False) -> str:
        """
        Get a random name from the specified time period.

        Args:
            time_period: Historical period to sample from
            raw: If True, returns name in original format, if False, converts to Title Case
        """
        period_data = self.name_data[time_period.value]
        names_data = period_data['names']

        names = []
        weights = []
        for name, info in names_data.items():
            names.append(name)
            weights.append(info['percentage'])

        name = random.choices(names, weights=weights, k=1)[0]
        return name if raw else name.title()
