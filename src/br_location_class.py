import json
from pathlib import Path

from src.br_name_class import BrazilianNameSampler, TimePeriod
import secrets


class BrazilianLocationSampler:
    """Brazilian location sampling class for generating realistic location data."""

    def __init__(self, json_file_path: str | Path, middle_names_path: str | Path | None = None):
        """Initialize the sampler with population data from JSON files.

        Args:
            json_file_path: Path to main JSON file with population data
            middle_names_path: Optional path to middle names JSON file

        Raises:
            ValueError: If required data is missing or invalid
            FileNotFoundError: If JSON files cannot be found
        """
        with Path(json_file_path).open(encoding='utf-8') as file:
            self.data = json.load(file)

        self.middle_names_path = middle_names_path

        # Ensure we have required data
        if 'common_names_percentage' not in self.data:
            raise ValueError("Missing 'common_names_percentage' data in JSON file")

        # Pre-calculate weights for more efficient sampling
        self._calculate_weights()

    def _calculate_weights(self) -> None:
        """Pre-calculate weights for states and cities based on population percentages."""
        # Calculate state weights
        self.state_weights = []
        self.state_names = []

        for state_name, state_data in self.data['states'].items():
            self.state_names.append(state_name)
            self.state_weights.append(state_data['population_percentage'])

        # Normalize state weights to sum to 1
        total_weight = sum(self.state_weights)
        self.state_weights = [w / total_weight for w in self.state_weights]

        # Calculate city weights per state
        self.city_weights_by_state = {}
        self.city_names_by_state = {}

        for city_name, city_data in self.data['cities'].items():
            state = city_data['city_uf']

            if state not in self.city_weights_by_state:
                self.city_weights_by_state[state] = []
                self.city_names_by_state[state] = []

            self.city_names_by_state[state].append(city_name)
            self.city_weights_by_state[state].append(city_data['population_percentage_state'])

        # Normalize city weights within each state
        for state in self.city_weights_by_state:
            total = sum(self.city_weights_by_state[state])
            if total > 0:
                self.city_weights_by_state[state] = [w / total for w in self.city_weights_by_state[state]]

    def get_state(self) -> tuple[str, str]:
        """Get a random state weighted by population percentage.

        Returns:
            Tuple of (state_name, state_abbreviation)
        """
        state_name = secrets.SystemRandom().choices(self.state_names, weights=self.state_weights, k=1)[0]
        state_abbr = self.data['states'][state_name]['state_abbr']
        return state_name, state_abbr

    def get_city(self, state_abbr: str | None = None) -> tuple[str, str]:
        """Get a random city weighted by population percentage.

        Args:
            state_abbr: Optional state abbreviation to get city from specific state

        Returns:
            Tuple of (city_name, state_abbreviation)

        Raises:
            ValueError: If no cities found for given state
        """
        if state_abbr is None:
            _, state_abbr = self.get_state()

        if state_abbr not in self.city_weights_by_state:
            raise ValueError(f'No cities found for state: {state_abbr}')

        city_name = secrets.SystemRandom().choices(self.city_names_by_state[state_abbr], weights=self.city_weights_by_state[state_abbr], k=1)[0]

        return city_name, state_abbr

    def get_state_and_city(self) -> tuple[str, str, str]:
        """Get a random state and city combination weighted by population percentage.

        Returns:
            Tuple of (state_name, state_abbreviation, city_name)
        """
        state_name, state_abbr = self.get_state()
        city_name, _ = self.get_city(state_abbr)
        return state_name, state_abbr, city_name

    def _normalize_cep(self, cep: str) -> int:
        """Convert CEP string to integer by removing dash.

        Args:
            cep: CEP string with or without dash

        Returns:
            Integer representation of CEP
        """
        return int(cep.replace('-', ''))

    def _format_cep(self, cep: int, with_dash: bool = True) -> str:
        """Format CEP integer back to string with optional dash.

        Args:
            cep: Integer CEP to format
            with_dash: Whether to include dash in formatted CEP

        Returns:
            Formatted CEP string
        """
        cep_str = str(cep).zfill(8)
        return f'{cep_str[:5]}-{cep_str[5:]}' if with_dash else cep_str

    def _get_random_cep_for_city(self, city_name: str) -> int:
        """Generate random CEP within city's range(s).

        Args:
            city_name: Name of city to generate CEP for

        Returns:
            Random valid CEP for given city
        """
        city_data = self.data['cities'][city_name]

        # Handle special cases with two ranges
        if city_name in ['São Paulo', 'Nova Iguaçu', 'Brasília']:
            # Randomly choose between the two ranges
            if secrets.SystemRandom().random() < 0.5:
                start = self._normalize_cep(city_data['cep_starts'])
                end = self._normalize_cep(city_data['cep_ends'])
            else:
                start = self._normalize_cep(city_data['cep_starts_two'])
                end = self._normalize_cep(city_data['cep_ends_two'])
        else:
            start = self._normalize_cep(city_data['cep_starts'])
            end = self._normalize_cep(city_data['cep_ends'])

        return secrets.SystemRandom().randint(start, end)

    def format_full_location(
        self, city: str, state: str, state_abbr: str, include_cep: bool = True, cep_without_dash: bool = False, name: str | None = None
    ) -> str:
        """Format location information into a single string.

        Args:
            city: City name
            state: State name
            state_abbr: State abbreviation
            include_cep: Whether to include CEP
            cep_without_dash: Whether to format CEP without dash
            name: Optional name to include

        Returns:
            Formatted location string
        """
        base = f'{city}, {state} ({state_abbr})'
        if not include_cep and not name:
            return base

        parts = [base]

        if include_cep:
            cep = self._get_random_cep_for_city(city)
            formatted_cep = self._format_cep(cep, not cep_without_dash)
            parts.append(formatted_cep)

        if name:
            parts.append(name)

        return ', '.join(parts)

    def get_random_location(
        self,
        city_only: bool = False,
        state_abbr_only: bool = False,
        state_full_only: bool = False,
        only_cep: bool = False,
        cep_without_dash: bool = False,
        time_period: TimePeriod = TimePeriod.UNTIL_2010,
        name_raw: bool = False,
        only_surname: bool = False,
        top_40: bool = False,
        always_middle: bool = False,
        only_middle: bool = False,
    ) -> str:
        """Get a random location with various formatting options.

        Args:
            city_only: Return only city name
            state_abbr_only: Return only state abbreviation
            state_full_only: Return only full state name
            only_cep: Return only CEP
            cep_without_dash: Format CEP without dash
            time_period: Time period for name sampling
            name_raw: Return name in raw format
            only_surname: Return only surname
            top_40: Use only top 40 surnames
            always_middle: Always include middle name
            only_middle: Return only middle name

        Returns:
            Formatted location string according to specified options
        """
        name_sampler = BrazilianNameSampler(self.data, self.middle_names_path)

        if only_middle:
            return name_sampler.get_random_name(raw=name_raw, only_middle=True)

        if only_surname:
            return name_sampler.get_random_surname(top_40, raw=name_raw)

        if only_cep:
            cep = self._get_random_cep_for_city(self.get_city()[0])
            return self._format_cep(cep, not cep_without_dash)

        if state_abbr_only:
            return self.get_state()[1]

        if state_full_only:
            return self.get_state()[0]

        if city_only:
            return self.get_city()[0]

        state_name, state_abbr, city_name = self.get_state_and_city()
        name = name_sampler.get_random_name(
            time_period=time_period, raw=name_raw, include_surname=True, top_40=top_40, always_middle=always_middle, only_middle=only_middle
        )
        return self.format_full_location(city_name, state_name, state_abbr, True, cep_without_dash, name)
