from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table

from src.time_period import TimePeriod
from src.brazilian_location_sampler import BrazilianLocationSampler
from src.brazilian_name_sampler import BrazilianNameSampler

app = typer.Typer(help='Brazilian Location and Name Sampler CLI')
console = Console()

# Define common options
DEFAULT_QTY = typer.Option(1, '--qty', '-q', help='Number of samples to generate')
JSON_PATH = typer.Option('population_data_2024_with_postalcodes.json', '--json-path', '-j', 
                        help='Path to the population data JSON file')

def create_results_table(results: list[str], title: str) -> Table:
    """Create a formatted table for displaying results."""
    table = Table(title=title)
    table.add_column('Index', justify='right', style='blue')
    table.add_column('Result', style='green')
    
    for idx, result in enumerate(results, 1):
        table.add_row(str(idx), result)
    
    return table

@app.command()
def names(
    qty: int = DEFAULT_QTY,
    time_period: TimePeriod = TimePeriod.UNTIL_2010,
    raw: bool = typer.Option(False, '--raw', '-r', help='Return names in raw format'),
    json_path: Path = JSON_PATH,
) -> list[str]:
    """Generate random Brazilian names."""
    try:
        sampler = BrazilianNameSampler(json_path)
        results = [sampler.get_random_name(time_period, raw) for _ in range(qty)]
        
        table = create_results_table(results, f'Random Brazilian Names ({time_period.value})')
        console.print(table)
        
        return results
    except Exception as e:
        console.print(f'[red]Error: {e}[/red]')
        raise typer.Exit(code=1)

@app.command()
def locations(
    qty: int = DEFAULT_QTY,
    city_only: bool = typer.Option(False, '--city-only', '-c', help='Return only city names'),
    state_abbr: bool = typer.Option(False, '--state-abbr', '-sa', help='Return only state abbreviations'),
    json_path: Path = JSON_PATH,
) -> list[str]:
    """Generate random Brazilian locations."""
    try:
        sampler = BrazilianLocationSampler(json_path)
        results = [
            sampler.get_random_location(city_only=city_only, state_abbr_only=state_abbr)
            for _ in range(qty)
        ]
        
        title = 'Random Brazilian '
        title += 'Cities' if city_only else 'State Abbreviations' if state_abbr else 'Locations'
        
        table = create_results_table(results, title)
        console.print(table)
        
        return results
    except Exception as e:
        console.print(f'[red]Error: {e}[/red]')
        raise typer.Exit(code=1)

def main():
    """Entry point for the CLI application"""
    app()

if __name__ == '__main__':
    main()
