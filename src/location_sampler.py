import json
import random
from pathlib import Path

from src.brazilian_name_sampler import BrazilianNameSampler
from src.time_period import TimePeriod


class BrazilianLocationSampler:
    def __init__(self, json_file_path: str | Path):
        """Initialize the sampler with population data from a JSON file."""
        with Path(json_file_path).open(encoding='utf-8') as file:
            self.data = json.load(file)

        # Ensure we have name data
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
        """Get a random state weighted by population percentage."""
        state_name = random.choices(self.state_names, weights=self.state_weights, k=1)[0]
        state_abbr = self.data['states'][state_name]['state_abbr']
        return state_name, state_abbr

    def get_city(self, state_abbr: str | None = None) -> tuple[str, str]:
        """Get a random city weighted by population percentage."""
        if state_abbr is None:
            _, state_abbr = self.get_state()

        if state_abbr not in self.city_weights_by_state:
            raise ValueError(f'No cities found for state: {state_abbr}')

        city_name = random.choices(self.city_names_by_state[state_abbr], weights=self.city_weights_by_state[state_abbr], k=1)[0]

        return city_name, state_abbr

    def get_state_and_city(self) -> tuple[str, str, str]:
        """Get a random state and city combination weighted by population percentage."""
        state_name, state_abbr = self.get_state()
        city_name, _ = self.get_city(state_abbr)
        return state_name, state_abbr, city_name

    def _normalize_cep(self, cep: str) -> int:
        """Convert CEP string to integer by removing dash."""
        return int(cep.replace('-', ''))

    def _format_cep(self, cep: int, with_dash: bool = True) -> str:
        """Format CEP integer back to string with optional dash."""
        cep_str = str(cep).zfill(8)
        return f'{cep_str[:5]}-{cep_str[5:]}' if with_dash else cep_str

    def _get_random_cep_for_city(self, city_name: str) -> int:
        """Generate random CEP within city's range(s)."""
        city_data = self.data['cities'][city_name]

        # Handle special cases with two ranges
        if city_name in ['São Paulo', 'Nova Iguaçu', 'Brasília']:
            # Randomly choose between the two ranges
            if random.random() < 0.5:
                start = self._normalize_cep(city_data['cep_starts'])
                end = self._normalize_cep(city_data['cep_ends'])
            else:
                start = self._normalize_cep(city_data['cep_starts_two'])
                end = self._normalize_cep(city_data['cep_ends_two'])
        else:
            start = self._normalize_cep(city_data['cep_starts'])
            end = self._normalize_cep(city_data['cep_ends'])

        return random.randint(start, end)

    def format_full_location(
        self,
        city: str,
        state: str,
        state_abbr: str,
        include_cep: bool = True,
        cep_without_dash: bool = False,
        name: str | None = None,
        no_parenthesis: bool = False,
    ) -> str:
        """Format location with optional CEP and name."""
        base = f'{city}, {state} {state_abbr if no_parenthesis else f"({state_abbr})"}'
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
        no_parenthesis: bool = False,
    ) -> str:
        """
        Get a random location with optional name.
        Now properly handles names using a dedicated name sampler instance.
        """
        # Create a name sampler instance for this request
        name_sampler = BrazilianNameSampler(self.data)

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
        name = name_sampler.get_random_name(time_period, raw=name_raw)
        return self.format_full_location(city_name, state_name, state_abbr, True, cep_without_dash, name, no_parenthesis)
import json
import random
from pathlib import Path

from src.brazilian_name_sampler import BrazilianNameSampler
from src.time_period import TimePeriod


class BrazilianLocationSampler:
    def __init__(self, json_file_path: str | Path):
        """Initialize the sampler with population data from a JSON file."""
        with Path(json_file_path).open(encoding='utf-8') as file:
            self.data = json.load(file)

        # Ensure we have name data
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
        """Get a random state weighted by population percentage."""
        state_name = random.choices(self.state_names, weights=self.state_weights, k=1)[0]
        state_abbr = self.data['states'][state_name]['state_abbr']
        return state_name, state_abbr

    def get_city(self, state_abbr: str | None = None) -> tuple[str, str]:
        """Get a random city weighted by population percentage."""
        if state_abbr is None:
            _, state_abbr = self.get_state()

        if state_abbr not in self.city_weights_by_state:
            raise ValueError(f'No cities found for state: {state_abbr}')

        city_name = random.choices(self.city_names_by_state[state_abbr], weights=self.city_weights_by_state[state_abbr], k=1)[0]

        return city_name, state_abbr

    def get_state_and_city(self) -> tuple[str, str, str]:
        """Get a random state and city combination weighted by population percentage."""
        state_name, state_abbr = self.get_state()
        city_name, _ = self.get_city(state_abbr)
        return state_name, state_abbr, city_name

    def _normalize_cep(self, cep: str) -> int:
        """Convert CEP string to integer by removing dash."""
        return int(cep.replace('-', ''))

    def _format_cep(self, cep: int, with_dash: bool = True) -> str:
        """Format CEP integer back to string with optional dash."""
        cep_str = str(cep).zfill(8)
        return f'{cep_str[:5]}-{cep_str[5:]}' if with_dash else cep_str

    def _get_random_cep_for_city(self, city_name: str) -> int:
        """Generate random CEP within city's range(s)."""
        city_data = self.data['cities'][city_name]

        # Handle special cases with two ranges
        if city_name in ['São Paulo', 'Nova Iguaçu', 'Brasília']:
            # Randomly choose between the two ranges
            if random.random() < 0.5:
                start = self._normalize_cep(city_data['cep_starts'])
                end = self._normalize_cep(city_data['cep_ends'])
            else:
                start = self._normalize_cep(city_data['cep_starts_two'])
                end = self._normalize_cep(city_data['cep_ends_two'])
        else:
            start = self._normalize_cep(city_data['cep_starts'])
            end = self._normalize_cep(city_data['cep_ends'])

        return random.randint(start, end)

    def format_full_location(
        self,
        city: str,
        state: str,
        state_abbr: str,
        include_cep: bool = True,
        cep_without_dash: bool = False,
        name: str | None = None,
        no_parenthesis: bool = False,
    ) -> str:
        """Format location with optional CEP and name."""
        base = f'{city}, {state} {state_abbr if no_parenthesis else f"({state_abbr})"}'
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
        no_parenthesis: bool = False,
    ) -> str:
        """
        Get a random location with optional name.
        Now properly handles names using a dedicated name sampler instance.
        """
        # Create a name sampler instance for this request
        name_sampler = BrazilianNameSampler(self.data)

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
        name = name_sampler.get_random_name(time_period, raw=name_raw)
        return self.format_full_location(city_name, state_name, state_abbr, True, cep_without_dash, name, no_parenthesis)
