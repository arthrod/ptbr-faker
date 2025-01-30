import json
import random
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help='Brazilian Location Sampler CLI')
console = Console()

# Define options at module level
DEFAULT_QTY = typer.Option(1, '--qty', '-q', help='Number of samples to generate')
CITY_ONLY = typer.Option(False, '--city-only', '-c', help='Return only city names')
STATE_ABBR_ONLY = typer.Option(False, '--state-abbr-only', '-sa', help='Return only state abbreviations')
STATE_FULL_ONLY = typer.Option(False, '--state-full-only', '-sf', help='Return only full state names')
JSON_PATH = typer.Option('population_data_2024_with_postalcodes.json', '--json-path', '-j', help='Path to the population data JSON file')
# Add these new options after the existing ones
CEP_WITHOUT_DASH = typer.Option(False, '--cep-without-dash', '-nd', help='Return CEP without dash')
ONLY_CEP = typer.Option(False, '--only-cep', '-oc', help='Return only CEP')


from src.sampler import BrazilianSampler

class BrazilianLocationSampler(BrazilianSampler):
    """Legacy class name maintained for backwards compatibility"""


def create_results_table(results: list[str], title: str) -> Table:
    """Create a formatted table for displaying results"""
    table = Table(title=title)
    table.add_column('Index', justify='right', style='blue')
    table.add_column('Location', style='yellow')

    for idx, result in enumerate(results, 1):
        table.add_row(str(idx), result)

    return table


@app.command()
def sample(
    qty: int | None = DEFAULT_QTY,
    city_only: bool = CITY_ONLY,
    state_abbr_only: bool = STATE_ABBR_ONLY,
    state_full_only: bool = STATE_FULL_ONLY,
    only_cep: bool = ONLY_CEP,
    cep_without_dash: bool = CEP_WITHOUT_DASH,
    json_path: Path = JSON_PATH,
) -> list[str]:
    """
    Generate random Brazilian location samples based on population-weighted distribution.
    Now includes CEP (postal code) functionality.
    """
    try:
        sampler = BrazilianLocationSampler(str(json_path))

        results = [
            sampler.get_random_location(
                city_only=city_only,
                state_abbr_only=state_abbr_only,
                state_full_only=state_full_only,
                only_cep=only_cep,
                cep_without_dash=cep_without_dash,
            )
            for _ in range(qty)
        ]

        title = 'Random Brazilian Location Samples'
        if city_only:
            title = 'Random Brazilian City Samples'
        elif state_abbr_only:
            title = 'Random Brazilian State Abbreviation Samples'
        elif state_full_only:
            title = 'Random Brazilian State Name Samples'
        elif only_cep:
            title = 'Random Brazilian CEP Samples'

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
