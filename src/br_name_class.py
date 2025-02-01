import json
import random
from enum import Enum
from pathlib import Path
from typing import Any


class TimePeriod(str, Enum):
    """Time periods available in the dataset"""

    UNTIL_1930 = 'ate1930'
    UNTIL_1940 = 'ate1940'
    UNTIL_1950 = 'ate1950'
    UNTIL_1960 = 'ate1960'
    UNTIL_1970 = 'ate1970'
    UNTIL_1980 = 'ate1980'
    UNTIL_1990 = 'ate1990'
    UNTIL_2000 = 'ate2000'
    UNTIL_2010 = 'ate2010'


class BrazilianNameSampler:
    # Dictionary mapping surnames to their prefixes and weights
    SURNAME_PREFIXES = {
        'SANTOS': [('dos', 0.85), ('de', 0.05)],
        'SILVA': [('da', 0.85), ('e', 0.05)],
        'NASCIMENTO': [('do', 0.9)],
        'COSTA': [('da', 0.9)],
        'SOUZA': [('de', 0.8)],
        'SOUSA': [('de', 0.8)],
        'OLIVEIRA': [('de', 0.8)],
        'JESUS': [('de', 0.8)],
        'PEREIRA': [('da', 0.6)],
        'FERREIRA': [('da', 0.6)],
        'LIMA': [('de', 0.6)],
        'CARVALHO': [('de', 0.6)],
        'RIBEIRO': [('do', 0.6)],
    }

    def __init__(self, json_file_path: str | Path | dict, middle_names_path: str | Path | None = None):
        """
        Initialize the name sampler with population data.
        Now accepts either a file path or pre-loaded data.

        Args:
            json_file_path: Path to JSON file or pre-loaded data dictionary
            middle_names_path: Path to middle names JSON file
        """
        if isinstance(json_file_path, str | Path):
            with Path(json_file_path).open(encoding='utf-8') as file:
                data = json.load(file)
        else:
            data = json_file_path

        if 'common_names_percentage' not in data:
            raise ValueError("Missing 'common_names_percentage' data")

        self.name_data = data['common_names_percentage']
        if 'surnames' not in data:
            raise ValueError("Missing 'surnames' data")

        self.surname_data = data['surnames']
        self.top_40_surnames = data['surnames'].get('top_40', {})

        # Load middle names data
        self.middle_names_data = self._load_middle_names(middle_names_path) if middle_names_path else None
        self._validate_data()

    def _load_middle_names(self, path: str | Path) -> dict[str, Any]:
        """Load middle names data from JSON file."""
        with Path(path).open(encoding='utf-8') as file:
            data = json.load(file)
            return data

    def _should_add_middle_name(self) -> bool:
        """Determine if a middle name should be added based on statistical data."""
        if not self.middle_names_data:
            return False
        return random.random() < (self.middle_names_data['percentage_with_second'] / 100)

    def _get_random_middle_name(self) -> str:
        """Get a random middle name based on frequency weights."""
        if not self.middle_names_data:
            return ''

        try:
            names = []
            weights = []
            total_weight = 0

            for name_data in self.middle_names_data['most_common']:
                names.append(name_data['name'])
                weight = float(name_data['percentage'])  # Ensure numeric conversion
                weights.append(weight)
                total_weight += weight

            if not names or total_weight <= 0:
                return ''

            return random.choices(names, weights=weights, k=1)[0]

        except (KeyError, ValueError, TypeError) as err:
            raise ValueError(f'Error processing middle names data: {err}') from err

    def get_random_name(
        self,
        time_period: TimePeriod = TimePeriod.UNTIL_2010,
        raw: bool = False,
        include_surname: bool = True,
        top_40: bool = False,
        with_only_one_surname: bool = False,  # This parameter needs to be explicitly handled
        always_middle: bool = False,
        only_middle: bool = False,
    ) -> str:
        """Get a random name from the specified time period."""
        if only_middle:
            middle_name = self._get_random_middle_name()
            return middle_name if raw else middle_name.title()

        period_data = self.name_data[time_period.value]
        names_data = period_data['names']

        names = []
        weights = []
        for name, info in names_data.items():
            names.append(name)
            weights.append(info['percentage'])

        name = random.choices(names, weights=weights, k=1)[0]

        # Handle middle name
        if always_middle or self._should_add_middle_name():
            middle_name = self._get_random_middle_name()
            name = f'{name} {middle_name}'

        if not include_surname:
            return name if raw else name.title()

        # Explicitly pass with_only_one_surname to get_random_surname
        surname = self.get_random_surname(top_40=top_40, raw=raw, with_only_one_surname=with_only_one_surname)
        return f'{name if raw else name.title()} {surname}'

    def _validate_data(self) -> None:
        """
        Validate the name data structure has all required time periods and correct format.
        """
        # Validate name data structure
        for period in TimePeriod:
            if period.value not in self.name_data:
                raise ValueError(f'Missing data for time period: {period.value}')

            period_data = self.name_data[period.value]
            if 'names' not in period_data:
                raise ValueError(f'Missing names data for time period: {period.value}')

            if not isinstance(period_data['names'], dict):
                raise TypeError(f'Invalid names data format for time period: {period.value}')

        # Validate surname data
        if not isinstance(self.surname_data, dict):
            raise TypeError('Invalid surname data format')

        # Validate middle names data if provided
        if self.middle_names_data:
            required_keys = {'total_people', 'total_with_second_names', 'percentage_with_second', 'most_common'}
            if not required_keys.issubset(self.middle_names_data.keys()):
                raise ValueError('Invalid middle names data structure. Missing required keys.')

            if not isinstance(self.middle_names_data['most_common'], list):
                raise TypeError("Invalid middle names data structure. 'most_common' must be a list.")

            if not self.middle_names_data['most_common']:
                raise ValueError("Middle names data contains no entries in 'most_common'.")

            for entry in self.middle_names_data['most_common']:
                if not {'name', 'count', 'percentage'}.issubset(entry.keys()):
                    raise ValueError('Invalid middle name entry structure. Missing required keys.')

    def _apply_prefix(self, surname: str) -> str:
        """
        Apply prefix to surname based on complex rules and probabilities.
        Supports multiple prefix options, compound surnames, and special cases.

        Args:
            surname: The surname to potentially prefix

        Returns:
            The surname with or without prefix based on probability rules

        Notes:
            - Handles case sensitivity consistently based on input format
            - Implements weighted probability for different prefix variations
            - Supports special cases for vowel-initial surnames
            - Maintains proper capitalization throughout the transformation
        """
        is_raw = surname.isupper()
        surname_upper = surname.upper()

        if surname_upper in self.SURNAME_PREFIXES:
            # Handle compound surname patterns first
            if surname_upper in ['SANTOS', 'SILVA']:
                compound_chance = random.random()
                compound_prefix = None  # Using a different variable name to avoid shadowing

                if compound_chance < 0.05:  # 5% chance for compound with "e"
                    compound_prefix = 'E' if is_raw else 'e'
                    return f'{surname} {compound_prefix}'

                if compound_chance < 0.15:  # Additional 10% chance for compound with "da/do"
                    compound_prefix = ('DA' if random.random() < 0.7 else 'DO') if is_raw else ('da' if random.random() < 0.7 else 'do')
                    return f'{surname} {compound_prefix}'

            # Regular prefix handling with multiple options
            prefix_options = self.SURNAME_PREFIXES[surname_upper]
            total_weight = sum(weight for _, weight in prefix_options)
            rand = random.random() * total_weight

            cumulative = 0
            for candidate_prefix, weight in prefix_options:  # Renamed loop variable to avoid shadowing
                cumulative += weight
                if rand <= cumulative:
                    final_prefix = candidate_prefix  # Store the selected prefix in a new variable

                    # Handle special cases for the selected prefix
                    if final_prefix in ['da', 'do'] and random.random() < 0.08:
                        final_prefix = ('DOS' if final_prefix == 'do' else 'DAS') if is_raw else ('dos' if final_prefix == 'do' else 'das')
                    elif final_prefix == 'de' and surname[0].lower() in 'aeiou' and random.random() < 0.7:
                        final_prefix = "D'" if is_raw else "d'"
                    else:
                        final_prefix = final_prefix.upper() if is_raw else final_prefix

                    return f'{final_prefix} {surname}'

        return surname

    def get_random_surname(self, top_40: bool = False, raw: bool = False, with_only_one_surname: bool = False) -> str:
        """
        Get random surname(s), optionally from top 40 only.

        Args:
            top_40: If True, only select from top 40 surnames
            raw: If True, returns surname in original format
            with_only_one_surname: If True, returns only one surname

        Returns:
            One or two surnames with appropriate prefixes
        """
        source = self.top_40_surnames if top_40 else self.surname_data
        surnames = []
        weights = []

        for surname, info in source.items():
            if surname != 'top_40':  # Skip the top_40 nested dictionary
                surnames.append(surname)
                weights.append(info['percentage'])

        # Get first surname
        surname1 = random.choices(surnames, weights=weights, k=1)[0]
        surname1 = surname1 if raw else surname1.title()
        surname1 = self._apply_prefix(surname1)

        if with_only_one_surname:
            return surname1

        # Get second surname
        surname2 = random.choices(surnames, weights=weights, k=1)[0]
        surname2 = surname2 if raw else surname2.title()
        surname2 = self._apply_prefix(surname2)

        return f'{surname1} {surname2}'
