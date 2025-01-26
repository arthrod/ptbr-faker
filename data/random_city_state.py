import json
import random
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help='Brazilian Population Sampler CLI')
console = Console()

# Define options at module level
DEFAULT_QTY = typer.Option(1, '--qty', '-q', help='Number of samples to generate')
CITY_ONLY = typer.Option(False, '--city-only', '-c', help='Return only city names')
STATE_ABBR_ONLY = typer.Option(False, '--state-abbr-only', '-sa', help='Return only state abbreviations')
STATE_FULL_ONLY = typer.Option(False, '--state-full-only', '-sf', help='Return only full state names')
JSON_PATH = typer.Option('population_data_2024.json', '--json-path', '-j', help='Path to the population data JSON file')


class BrazilianPopulationSampler:
    def __init__(self, json_file_path: str):
        """
        Initialize the sampler with population data from a JSON file.

        Args:
            json_file_path (str): Path to the JSON file containing population data
        """
        with Path(json_file_path).open(encoding='utf-8') as file:
            self.data = json.load(file)

        # Pre-calculate weights for more efficient sampling
        self._calculate_weights()

    def _calculate_weights(self) -> None:
        """
        Pre-calculate weights for states and cities based on population percentages.
        Stores the results in instance variables for reuse.
        """
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

    def format_full_location(self, city: str, state: str, state_abbr: str) -> str:
        """Format location in the standard format: City, State (STATE_ABBR)"""
        return f'{city}, {state} ({state_abbr})'

    def get_random_location(self, city_only: bool = False, state_abbr_only: bool = False, state_full_only: bool = False) -> str:
        """
        Get a random location based on the specified format.

        Args:
            city_only: Return only the city name
            state_abbr_only: Return only the state abbreviation
            state_full_only: Return only the full state name

        Returns:
            Formatted location string based on specified parameters
        """
        if state_abbr_only:
            return self.get_state()[1]
        if state_full_only:
            return self.get_state()[0]
        if city_only:
            return self.get_city()[0]
        state_name, state_abbr, city_name = self.get_state_and_city()
        return self.format_full_location(city_name, state_name, state_abbr)


def create_results_table(results: list[str], title: str) -> Table:
    """Create a formatted table for displaying results"""
    table = Table(title=title)
    table.add_column('Index', justify='right', style='cyan')
    table.add_column('Location', style='green')

    for idx, result in enumerate(results, 1):
        table.add_row(str(idx), result)

    return table


@app.command()
def sample(
    qty: int | None = DEFAULT_QTY,
    city_only: bool = CITY_ONLY,
    state_abbr_only: bool = STATE_ABBR_ONLY,
    state_full_only: bool = STATE_FULL_ONLY,
    json_path: Path = JSON_PATH,
) -> list[str]:
    """
    Generate random Brazilian location samples based on population-weighted distribution.
    Returns formatted locations based on specified parameters.
    """
    try:
        # Initialize sampler
        sampler = BrazilianPopulationSampler(str(json_path))

        # Generate results
        results = [
            sampler.get_random_location(city_only=city_only, state_abbr_only=state_abbr_only, state_full_only=state_full_only)
            for _ in range(qty)
        ]

        # Create and display results table
        title = 'Random Location Samples'
        if city_only:
            title = 'Random City Samples'
        elif state_abbr_only:
            title = 'Random State Abbreviation Samples'
        elif state_full_only:
            title = 'Random State Name Samples'

        table = create_results_table(results, title)
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
