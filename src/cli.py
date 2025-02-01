from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from src.br_location_class import BrazilianLocationSampler
from src.br_name_class import BrazilianNameSampler, TimePeriod
from src.document_sampler import DocumentSampler

app = typer.Typer(help='Brazilian Location, Name and Document Sampler CLI')
console = Console()

# Define options at module level
DEFAULT_QTY = typer.Option(1, '--qty', '-q', help='Number of samples to generate')
CITY_ONLY = typer.Option(False, '--city-only', '-c', help='Return only city names')
STATE_ABBR_ONLY = typer.Option(False, '--state-abbr-only', '-sa', help='Return only state abbreviations')
STATE_FULL_ONLY = typer.Option(False, '--state-full-only', '-sf', help='Return only full state names')
JSON_PATH = typer.Option(
    '/Users/arthrod/Library/CloudStorage/GoogleDrive-arthursrodrigues@gmail.com/My Drive/acode/atemp-drive/ptbr-faker/data/split_data/br_pop_data_2024_names_cities.json',
    '--json-path',
    '-j',
    help='Path to the population data JSON file',
)
MIDDLE_NAMES_PATH = typer.Option(
    '/Users/arthrod/Library/CloudStorage/GoogleDrive-arthursrodrigues@gmail.com/My Drive/acode/atemp-drive/ptbr-faker/data/split_data/middle_names.json',
    '--middle-names-path',
    '-m',
    help='Path to the middle names JSON file',
)
CEP_WITHOUT_DASH = typer.Option(False, '--cep-without-dash', '-nd', help='Return CEP without dash')
ONLY_CEP = typer.Option(False, '--only-cep', '-oc', help='Return only CEP')
TIME_PERIOD = typer.Option(TimePeriod.UNTIL_2010, '--time-period', '-t', help='Time period for name sampling')
RETURN_ONLY_NAME = typer.Option(False, '--return-only-name', '-n', help='Return only the name without location')
NAME_RAW = typer.Option(False, '--name-raw', '-r', help='Return names in raw format (all caps)')
ONLY_SURNAME = typer.Option(False, '--only-surname', '-s', help='Return only surname')
TOP_40 = typer.Option(False, '--top-40', '-t40', help='Use only top 40 surnames')
WITH_ONLY_ONE_SURNAME = typer.Option(False, '--one-surname', '-os', help='Return only one surname instead of two')
ALWAYS_MIDDLE = typer.Option(False, '--always-middle', '-am', help='Always include a middle name')
ONLY_MIDDLE = typer.Option(False, '--only-middle', '-om', help='Return only middle name')
ALWAYS_CPF = typer.Option(True, '--always-cpf', '-ac', help='Always include CPF')
ALWAYS_PIS = typer.Option(True, '--always-pis', '-ap', help='Always include PIS')
ALWAYS_CNPJ = typer.Option(False, '--always-cnpj', '-acn', help='Always include CNPJ')
ALWAYS_CEI = typer.Option(False, '--always-cei', '-ace', help='Always include CEI')
ONLY_CPF = typer.Option(False, '--only-cpf', '-oc', help='Return only CPF')
ONLY_PIS = typer.Option(False, '--only-pis', '-op', help='Return only PIS')
ONLY_CNPJ = typer.Option(False, '--only-cnpj', '-ocn', help='Return only CNPJ')
ONLY_CEI = typer.Option(False, '--only-cei', '-oce', help='Return only CEI')


def create_results_table(
    results: list[str],
    title: str,
    documents: list[dict] | None = None,
    return_only_name: bool = False,
    only_location: bool = False,
    only_document: bool = False,
) -> Table:
    """Create a formatted table for displaying Brazilian sample data results.

    This function creates a richly formatted table that can display various combinations of:
    - Names (first name, middle name, surnames)
    - Locations (cities, states, CEP)
    - Documents (CPF, PIS, CNPJ, CEI)

    The table adapts its columns and formatting based on the type of data being displayed:
    - For names: Shows first name + middle name in one row, surnames in another
    - For documents: CPF and PIS are displayed on separate lines within the same cell
    - For locations: City and state information is properly formatted

    Args:
        results: List of generated sample strings to display
        title: Table title describing the type of data
        documents: Optional list of document dictionaries containing CPF, PIS, CNPJ, CEI
        return_only_name: Flag indicating if only names should be displayed
        only_location: Flag indicating if only location data should be displayed
        only_document: Flag indicating if only document data should be displayed

    Returns:
        Rich Table object formatted according to the data type and options
    """
    table = Table(title=title)

    # Add index column for all table types
    table.add_column('Index', justify='right', style='blue', no_wrap=True)

    # Configure columns based on display mode
    if only_document:
        # Document-only table
        table.add_column('Documents', style='magenta')
    else:
        # Add name columns if we're not only showing locations
        if not only_location:
            table.add_column('First Name & Middle', style='green')
            table.add_column('Surname', style='green')

        # Add location column if we're not only showing names
        if not return_only_name:
            table.add_column('Place', style='yellow')

        # Add documents column if documents are provided
        if documents:
            table.add_column('Documents', style='magenta')

    # Process each result and add rows to the table
    for idx, item in enumerate(zip(results, documents or [{}] * len(results)), 1):
        result, doc = item

        if only_document:
            # Format document-only display
            doc_lines = []
            if doc.get('cpf'):
                doc_lines.append(f"CPF: {doc['cpf']}")
            if doc.get('pis'):
                doc_lines.append(f"PIS: {doc['pis']}")
            if doc.get('cnpj'):
                doc_lines.append(f"CNPJ: {doc['cnpj']}")
            if doc.get('cei'):
                doc_lines.append(f"CEI: {doc['cei']}")
            table.add_row(str(idx), '\n'.join(doc_lines))

        elif return_only_name:
            # Format name-only display
            names = result.split(' ')
            if len(names) > 1:
                # Split into first/middle and surnames
                first_middle = ' '.join(names[:-1])
                surname = names[-1]
                table.add_row(str(idx), first_middle, surname)
            else:
                table.add_row(str(idx), names[0], '')

        elif only_location:
            # Format location-only display
            table.add_row(str(idx), result)

        else:
            # Format combined display (names + location + documents)
            parts = result.rsplit(', ', 1)
            if len(parts) == 2:
                place, full_name = parts

                # Split name into components
                names = full_name.split(' ')
                if len(names) > 1:
                    first_middle = ' '.join(names[:-1])  # First name and middle names
                    surname = names[-1]  # Last name(s)
                else:
                    first_middle = names[0]
                    surname = ''

                # Prepare document lines if present
                doc_lines = []
                if doc.get('cpf'):
                    doc_lines.append(f"CPF: {doc['cpf']}")
                if doc.get('pis'):
                    doc_lines.append(f"PIS: {doc['pis']}")
                if doc.get('cnpj'):
                    doc_lines.append(f"CNPJ: {doc['cnpj']}")
                if doc.get('cei'):
                    doc_lines.append(f"CEI: {doc['cei']}")

                # Build row based on which columns are present
                row = [str(idx), first_middle, surname]
                if not return_only_name:
                    row.append(place)
                if documents:
                    row.append('\n'.join(doc_lines))

                table.add_row(*row)
            else:
                # Handle cases where the result doesn't split into place and name
                table.add_row(str(idx), '', '', result)

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
    middle_names_path: Path = MIDDLE_NAMES_PATH,
    only_surname: bool = ONLY_SURNAME,
    top_40: bool = TOP_40,
    with_only_one_surname: bool = WITH_ONLY_ONE_SURNAME,
    always_middle: bool = ALWAYS_MIDDLE,
    only_middle: bool = ONLY_MIDDLE,
    # Document generation flags
    always_cpf: bool = True,
    always_pis: bool = True,
    always_cnpj: bool = False,
    always_cei: bool = False,
    only_cpf: bool = False,
    only_pis: bool = False,
    only_cnpj: bool = False,
    only_cei: bool = False,
) -> tuple[list[str], list[dict]]:
    try:
        doc_sampler = DocumentSampler()
        documents = []

        # Handle document-only requests first
        if any([only_cpf, only_pis, only_cnpj, only_cei]):
            documents = []
            for _ in range(qty):
                doc = {}
                if only_cpf:
                    doc['cpf'] = doc_sampler.generate_cpf()
                if only_pis:
                    doc['pis'] = doc_sampler.generate_pis()
                if only_cnpj:
                    doc['cnpj'] = doc_sampler.generate_cnpj()
                if only_cei:
                    doc['cei'] = doc_sampler.generate_cei()
                documents.append(doc)

            results = [','.join(doc.values()) for doc in documents]
            title = 'Brazilian Document Samples'

        elif return_only_name or only_surname or only_middle:
            # Name-only generation using BrazilianNameSampler
            sampler = BrazilianNameSampler(json_path, middle_names_path)

            if only_surname:
                results = [
                    sampler.get_random_surname(top_40=top_40, raw=name_raw, with_only_one_surname=with_only_one_surname) for _ in range(qty)
                ]
            elif only_middle:
                results = [sampler.get_random_name(raw=name_raw, only_middle=True) for _ in range(qty)]
            else:
                results = [
                    sampler.get_random_name(
                        time_period=time_period,
                        raw=name_raw,
                        include_surname=True,
                        top_40=top_40,
                        with_only_one_surname=with_only_one_surname,
                        always_middle=always_middle,
                    )
                    for _ in range(qty)
                ]

            # Add documents for name-only results if not only_middle/only_surname
            if not (only_middle or only_surname):
                for _ in range(qty):
                    doc = {}
                    if always_cpf:
                        doc['cpf'] = doc_sampler.generate_cpf()
                    if always_pis:
                        doc['pis'] = doc_sampler.generate_pis()
                    if always_cnpj:
                        doc['cnpj'] = doc_sampler.generate_cnpj()
                    if always_cei:
                        doc['cei'] = doc_sampler.generate_cei()
                    documents.append(doc)

        else:
            # Location generation (with optional names) using BrazilianLocationSampler
            sampler = BrazilianLocationSampler(json_path, middle_names_path)
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
                    always_middle=always_middle,
                    only_middle=only_middle,
                )
                for _ in range(qty)
            ]

            # Add documents for location results
            for _ in range(qty):
                doc = {}
                if always_cpf:
                    doc['cpf'] = doc_sampler.generate_cpf()
                if always_pis:
                    doc['pis'] = doc_sampler.generate_pis()
                if always_cnpj:
                    doc['cnpj'] = doc_sampler.generate_cnpj()
                if always_cei:
                    doc['cei'] = doc_sampler.generate_cei()
                documents.append(doc)

        # Determine appropriate title based on options
        title = 'Random Brazilian Samples'
        if only_middle:
            title = 'Random Brazilian Middle Names'
        elif only_surname:
            title = f'Random Brazilian Surnames{" (Top 40)" if top_40 else ""}{" (Single)" if with_only_one_surname else ""}'
        elif return_only_name:
            title = (
                f'Random Brazilian Names{" with Middle Names" if always_middle else ""}'
                f'{" with Single" if with_only_one_surname else " with"} Surname'
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

        # Create and display results table
        only_location = any([city_only, state_abbr_only, state_full_only, only_cep])
        table = create_results_table(
            results=results,
            title=title,
            documents=documents,
            return_only_name=return_only_name or only_surname or only_middle,
            only_location=only_location,
        )
        console.print(table)

        return results, documents

    except Exception as e:
        console.print(f'[red]Error: {e!s}[/red]')
        raise typer.Exit(code=1) from e


def main():
    """Entry point for the CLI application"""
    app()


if __name__ == '__main__':
    main()
