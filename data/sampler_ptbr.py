import json
from enum import Enum
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
import secrets

app = typer.Typer(help='Brazilian Location and Name Sampler CLI')
console = Console()


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


# Define options at module level
DEFAULT_QTY = typer.Option(1, '--qty', '-q', help='Number of samples to generate')
CITY_ONLY = typer.Option(False, '--city-only', '-c', help='Return only city names')
STATE_ABBR_ONLY = typer.Option(False, '--state-abbr-only', '-sa', help='Return only state abbreviations')
STATE_FULL_ONLY = typer.Option(False, '--state-full-only', '-sf', help='Return only full state names')
JSON_PATH = typer.Option(
    'population_data_2024_with_postalcodes_updated.json', '--json-path', '-j', help='Path to the population data JSON file'
)
CEP_WITHOUT_DASH = typer.Option(False, '--cep-without-dash', '-nd', help='Return CEP without dash')
ONLY_CEP = typer.Option(False, '--only-cep', '-oc', help='Return only CEP')
TIME_PERIOD = typer.Option(TimePeriod.UNTIL_2010, '--time-period', '-t', help='Time period for name sampling')
RETURN_ONLY_NAME = typer.Option(False, '--return-only-name', '-n', help='Return only the name without location')
# Add this with the other options at the top of the file
NAME_RAW = typer.Option(False, '--name-raw', '-r', help='Return names in raw format (all caps)')
ONLY_SURNAME = typer.Option(False, '--only-surname', '-s', help='Return only surname')
TOP_40 = typer.Option(False, '--top-40', '-t40', help='Use only top 40 surnames')
WITH_ONLY_ONE_SURNAME = typer.Option(False, '--one-surname', '-os', help='Return only one surname instead of two')


class BrazilianNameSampler:
    # Dictionary mapping surnames to their prefixes and weights
    SURNAME_PREFIXES = {
        'SANTOS': ('dos', 0.9),
        'SILVA': ('da', 0.9),
        'NASCIMENTO': ('do', 0.9),
        'COSTA': ('da', 0.9),
        'SOUZA': ('de', 0.8),
        'SOUSA': ('de', 0.8),
        'OLIVEIRA': ('de', 0.8),
        'JESUS': ('de', 0.8),
        'PEREIRA': ('da', 0.6),
        'FERREIRA': ('da', 0.6),
        'LIMA': ('de', 0.6),
        'CARVALHO': ('de', 0.6),
        'RIBEIRO': ('do', 0.6),
    }

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

        print(f"Loaded data type: {type(data)}")
        if 'common_names_percentage' not in data:
            raise ValueError("Missing 'common_names_percentage' data")

        self.name_data = data['common_names_percentage']
        print(f"Name data type: {type(self.name_data)}")
        print(f"Name data keys: {list(self.name_data.keys()) if isinstance(self.name_data, dict) else 'Not a dict'}")
        if 'surnames' not in data:
            raise ValueError("Missing 'surnames' data")

        self.surname_data = data['surnames']
        self.top_40_surnames = data['surnames'].get('top_40', {})
        self._validate_data()

    def _validate_data(self) -> None:
        """
        Validate the name data structure has all required time periods and correct format.

        Raises:
            ValueError: If any required data structure is missing or invalid
        """
        for period in TimePeriod:
            print(f"Validating period {period.value}")
            if period.value not in self.name_data:
                raise ValueError(f'Missing data for time period: {period.value}')

            period_data = self.name_data[period.value]
            print(f"Period data type for {period.value}: {type(period_data)}")
            print(f"Period data value: {period_data}")
            
            if not isinstance(period_data, dict):
                raise ValueError(f"Period data must be a dictionary, got {type(period_data)} for {period.value}")
                
            if not {'names', 'total'}.issubset(period_data.keys()):
                raise ValueError(f"Invalid data structure for period {period.value}. Must contain 'names' and 'total'")

        # Validate surname data structure
        if not isinstance(self.surname_data, dict):
            raise ValueError("Invalid 'surnames' data structure")

    def _apply_prefix(self, surname: str) -> str:
        """
        Apply prefix to surname based on predefined rules and probabilities.

        Args:
            surname: The surname to potentially prefix

        Returns:
            The surname with or without prefix based on probability
        """
        surname_upper = surname.upper()
        if surname_upper in self.SURNAME_PREFIXES:
            prefix, weight = self.SURNAME_PREFIXES[surname_upper]
            if secrets.SystemRandom().random() < weight:
                return f'{prefix} {surname}'
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
        surname1 = secrets.SystemRandom().choices(surnames, weights=weights, k=1)[0]
        surname1 = surname1 if raw else surname1.title()
        surname1 = self._apply_prefix(surname1)

        if with_only_one_surname:
            return surname1

        # Get second surname
        surname2 = secrets.SystemRandom().choices(surnames, weights=weights, k=1)[0]
        surname2 = surname2 if raw else surname2.title()
        surname2 = self._apply_prefix(surname2)

        return f'{surname1} {surname2}'

    def get_random_name(
        self,
        time_period: TimePeriod = TimePeriod.UNTIL_2010,
        raw: bool = False,
        include_surname: bool = True,
        top_40: bool = False,
        with_only_one_surname: bool = False,
    ) -> str:
        """Get a random name from the specified time period."""
        print(f"Time period: {time_period.value}")
        print(f"Name data type before access: {type(self.name_data)}")
        print(f"Period data for {time_period.value}: {self.name_data[time_period.value]}")
        period_data = self.name_data[time_period.value]
        print(f"Period data type: {type(period_data)}")
        if not isinstance(period_data, dict):
            raise ValueError(f"Expected period_data to be a dict, got {type(period_data)} with value: {period_data}")
        names_data = period_data['names']
        names = []
        weights = []
        for name, info in names_data.items():
            names.append(name)
            weights.append(info['percentage'])

        name = secrets.SystemRandom().choices(names, weights=weights, k=1)[0]
        if not include_surname:
            return name if raw else name.title()

        surname = self.get_random_surname(top_40, raw, with_only_one_surname)
        return f'{name if raw else name.title()} {surname}'


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
        state_name = secrets.SystemRandom().choices(self.state_names, weights=self.state_weights, k=1)[0]
        state_abbr = self.data['states'][state_name]['state_abbr']
        return state_name, state_abbr

    def get_city(self, state_abbr: str | None = None) -> tuple[str, str]:
        """Get a random city weighted by population percentage."""
        if state_abbr is None:
            _, state_abbr = self.get_state()

        if state_abbr not in self.city_weights_by_state:
            raise ValueError(f'No cities found for state: {state_abbr}')

        city_name = secrets.SystemRandom().choices(self.city_names_by_state[state_abbr], weights=self.city_weights_by_state[state_abbr], k=1)[0]

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
        """Format location with optional CEP and name."""
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
    ) -> str:
        """Get a random location with optional name/surname."""
        name_sampler = BrazilianNameSampler(self.data)

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
        name = name_sampler.get_random_name(time_period, raw=name_raw, include_surname=True, top_40=top_40)
        return self.format_full_location(city_name, state_name, state_abbr, True, cep_without_dash, name)


def create_results_table(results: list[str], title: str, return_only_name: bool = False, only_location: bool = False) -> Table:
    """
    Create a formatted table for displaying results with dynamic columns based on content.
    """
    table = Table(title=title)
    table.add_column('Index', justify='right', style='blue', no_wrap=True)

    # Add columns based on what we're displaying
    if not only_location:
        table.add_column('Name', style='green')
    if not return_only_name:
        table.add_column('Place', style='yellow')

    for idx, result in enumerate(results, 1):
        if return_only_name:
            # Only name, single column plus index
            table.add_row(str(idx), result)
        elif only_location:
            # Only location/place info, single column plus index
            table.add_row(str(idx), result)
        else:
            # Both name and place
            parts = result.rsplit(', ', 1)
            if len(parts) == 2:
                place, name = parts
                if name.replace('-', '').isdigit():  # It's a CEP
                    table.add_row(str(idx), '', result)
                else:
                    table.add_row(str(idx), name, place)
            else:
                table.add_row(str(idx), '', result)

    return table


@app.command()
def sample(
    qty: int = DEFAULT_QTY,
    city_only: bool = CITY_ONLY,
    state_abbr_only: bool = STATE_ABBR_ONLY,
    state_full_only: bool = STATE_FULL_ONLY,
    only_cep: bool = ONLY_CEP,
    cep_without_dash: bool = CEP_WITHOUT_DASH,
    time_period: TimePeriod = TIME_PERIOD,
    return_only_name: bool = RETURN_ONLY_NAME,
    name_raw: bool = NAME_RAW,
    json_path: Path = JSON_PATH,
    only_surname: bool = ONLY_SURNAME,
    top_40: bool = TOP_40,
    with_only_one_surname: bool = WITH_ONLY_ONE_SURNAME,
) -> list[str]:
    try:
        if return_only_name or only_surname:
            sampler = BrazilianNameSampler(json_path)
            if only_surname:
                results = [
                    sampler.get_random_surname(top_40=top_40, raw=name_raw, with_only_one_surname=with_only_one_surname) for _ in range(qty)
                ]
            else:
                results = [
                    sampler.get_random_name(
                        time_period=time_period,
                        raw=name_raw,
                        include_surname=True,
                        top_40=top_40,
                        with_only_one_surname=with_only_one_surname,
                    )
                    for _ in range(qty)
                ]
        else:
            sampler = BrazilianLocationSampler(json_path)
            results = [
                sampler.get_random_location(
                    city_only=city_only,
                    state_abbr_only=state_abbr_only,
                    state_full_only=state_full_only,
                    only_cep=only_cep,
                    cep_without_dash=cep_without_dash,
                    time_period=time_period,
                    name_raw=name_raw,
                    only_surname=only_surname,
                    top_40=top_40,
                )
                for _ in range(qty)
            ]

        # Set appropriate title and create table
        title = 'Random Brazilian Samples'
        if only_surname:
            title = f'Random Brazilian Surnames{" (Top 40)" if top_40 else ""}{" (Single)" if with_only_one_surname else ""}'
        elif return_only_name:
            title = (
                f'Random Brazilian Names with {"Single " if with_only_one_surname else ""}Surname'
                f' ({time_period.value}{"- Top 40" if top_40 else ""})'
            )
        elif city_only:
            title = 'Random Brazilian City Samples'
        elif state_abbr_only:
            title = 'Random Brazilian State Abbreviation Samples'
        elif state_full_only:
            title = 'Random Brazilian State Name Samples'
        elif only_cep:
            title = 'Random Brazilian CEP Samples'

        # Create and display results
        only_location = any([city_only, state_abbr_only, state_full_only, only_cep])
        table = create_results_table(results=results, title=title, return_only_name=return_only_name, only_location=only_location)
        console.print(table)

        return results

    except Exception as e:
        console.print(f'[red]Error: {e!s}[/red]')
        raise typer.Exit(code=1) from e


def main():
    """Entry point for the CLI application"""
    app()


if __name__ == '__main__':
    main()
