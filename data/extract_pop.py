# AI!I need to extract the data from excel using duckdb. I got this error, make this extraction happen! An error occurred during population data extraction: HTTP Error: Failed to download extension "st_read" at URL "http://extensions.duckdb.org/v1.1.3/osx_arm64/st_read.duckdb_extension.gz" (HTTP 403) Candidate extensions: "postgres", "postgres_scanner", "substrait", "sqlite_scanner", "spatial" HELP!!

import json
from pathlib import Path

import duckdb
import ibis  # noqa: F401


def create_population_dict():
    # Initialize DuckDB and Spatial extension
    df = duckdb.connect()

    # Install the 'spatial' extension (only needed once)
    try:
        df.execute("INSTALL 'spatial';")
        print('Spatial extension installed successfully.')
    except duckdb.CatalogException as e:
        if 'already installed' in str(e).lower():
            print('Spatial extension is already installed.')
        else:
            print(f'Error installing spatial extension: {e}')
            raise e

    # Load the 'spatial' extension
    try:
        df.execute("LOAD 'spatial';")
        print('Spatial extension loaded successfully.')
    except duckdb.CatalogException as e:
        print(f'Error loading spatial extension: {e}')
        raise e

    # Define the path to your Excel file
    excel_file_path = Path('estimativa_dou_2024.xls').resolve()  # Ensure the file is in the current directory or provide the absolute path
    if not excel_file_path.exists():
        print(f'Error: Excel file not found at {excel_file_path}')
        raise FileNotFoundError(f'Excel file not found at {excel_file_path}')
    excel_file_str = str(excel_file_path)
    print(f'Using Excel file at: {excel_file_str}')

    # Create 'states' table from Excel sheet using 'read_excel'
    try:
        df.execute(
            f"""
            CREATE OR REPLACE TABLE states AS
            SELECT * FROM read_excel(
                '{excel_file_str}',
                sheetname='BRASIL E UFs',
                header=true
            )
            LIMIT 28
        """
        )
        print("Table 'states' created successfully.")
    except duckdb.CatalogException as e:
        print(f"Error creating 'states' table: {e}")
        raise e

    # Create 'cities' table from Excel sheet using 'read_excel'
    try:
        df.execute(
            f"""
            CREATE OR REPLACE TABLE cities AS
            SELECT * FROM read_excel(
                '{excel_file_str}',
                sheetname='MUNICÍPIOS',
                header=true
            )
        """
        )
        print("Table 'cities' created successfully.")
    except duckdb.CatalogException as e:
        print(f"Error creating 'cities' table: {e}")
        raise e

    # Initialize the result dictionary
    result = {
        'brasil': {},
        'regions': {},
        'states': {},
        'cities': {},
    }

    # Populate 'brasil' total population
    try:
        brasil_pop = df.execute("SELECT column2 FROM states WHERE column1='Brasil';").fetchone()[0]
        result['brasil']['total_population'] = brasil_pop
        print(f"'brasil' total population: {brasil_pop}")
    except duckdb.CatalogException as e:
        print(f"Error querying 'brasil' population: {e}")
        raise e
    except TypeError as e:
        print(f"No data found for 'Brasil': {e}")
        raise e

    # Add regions
    regions_query = """
        SELECT column1 AS region, column2 AS population 
        FROM states 
        WHERE column1 IN ('Norte', 'Nordeste', 'Sudeste', 'Sul', 'Centro-Oeste')
    """
    try:
        regions = df.execute(regions_query).fetchall()
        for region, pop in regions:
            result['regions'][region.lower()] = {'total_population_per_region': pop}
        print('Regions added to result.')
    except duckdb.CatalogException as e:
        print(f'Error querying regions: {e}')
        raise e

    # Add states with mapping
    state_mapping = {
        'Rondônia': 'RO',
        'Acre': 'AC',
        'Amazonas': 'AM',
        'Roraima': 'RR',
        'Pará': 'PA',
        'Amapá': 'AP',
        'Tocantins': 'TO',
        'Maranhão': 'MA',
        'Piauí': 'PI',
        'Ceará': 'CE',
        'Rio Grande do Norte': 'RN',
        'Paraíba': 'PB',
        'Pernambuco': 'PE',
        'Alagoas': 'AL',
        'Sergipe': 'SE',
        'Bahia': 'BA',
        'Minas Gerais': 'MG',
        'Espírito Santo': 'ES',
        'Rio de Janeiro': 'RJ',
        'São Paulo': 'SP',
        'Paraná': 'PR',
        'Santa Catarina': 'SC',
        'Rio Grande do Sul': 'RS',
        'Mato Grosso do Sul': 'MS',
        'Mato Grosso': 'MT',
        'Goiás': 'GO',
        'Distrito Federal': 'DF',
    }

    try:
        total_pop = result['brasil']['total_population']
    except KeyError as e:
        print(f"KeyError accessing 'brasil' population: {e}")
        raise e

    states_query = """
        SELECT column1, column2 
        FROM states 
        WHERE column1 NOT IN ('Brasil', 'Norte', 'Nordeste', 'Sudeste', 'Sul', 'Centro-Oeste')
    """

    try:
        states = df.execute(states_query).fetchall()
        for state, pop in states:
            if state not in state_mapping:
                print(f"Warning: State '{state}' not found in state_mapping.")
                continue  # Skip or handle as needed
            result['states'][state] = {
                'state_abbr': state_mapping[state],
                'state_population': pop,
                'population_percentage': round(float(pop) / total_pop * 100, 2),
            }
        print('States added to result.')
    except duckdb.CatalogException as e:
        print(f'Error querying states: {e}')
        raise e

    # Add cities
    cities_query = 'SELECT * FROM cities'
    try:
        cities = df.execute(cities_query).fetchall()
        for row in cities:
            # Adjust indices based on actual column positions
            if len(row) < 5:
                print(f'Warning: Incomplete row data: {row}')
                continue
            city_name = row[3]
            result['cities'][city_name] = {
                'city_uf': row[0],
                'uf_code': row[1],
                'city_code': str(row[2]).zfill(5),
                'city_population': row[4],
            }
        print('Cities added to result.')
    except duckdb.CatalogException as e:
        print(f'Error querying cities: {e}')
        raise e

    # Save to JSON file
    try:
        with Path('population_data.json').open('w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print("Result saved to 'population_data.json'.")
    except Exception as e:
        print(f'Error saving JSON file: {e}')
        raise e

    return result


if __name__ == '__main__':
    try:
        data = create_population_dict()
    except Exception as e:
        print(f'An error occurred during population data extraction: {e}')
