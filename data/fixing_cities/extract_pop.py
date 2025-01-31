import json
from pathlib import Path

import duckdb


def create_population_dict():
    df = duckdb.connect()
    df.execute("INSTALL 'spatial';")
    df.execute("LOAD 'spatial';")

    excel_file_path = Path('estimativa_dou_2024.xlsx')
    excel_file_str = str(excel_file_path)

    # Create states table - note we use the long column name from our test results
    df.execute(f"""
        CREATE OR REPLACE TABLE states AS 
        SELECT 
            "ESTIMATIVAS DA POPULAÇÃO RESIDENTE NO BRASIL E UNIDADES DA FEDERAÇÃO COM DATA DE REFERÊNCIA EM 1º DE JULHO DE 2024" as name,
            CAST(Field2 AS BIGINT) as population
        FROM ST_read(
            '{excel_file_str}', 
            layer='BRASIL E UFs',
            open_options=['HEADERS=FORCE']
        )
        WHERE "ESTIMATIVAS DA POPULAÇÃO RESIDENTE NO BRASIL E UNIDADES DA FEDERAÇÃO COM DATA DE REFERÊNCIA EM 1º DE JULHO DE 2024" NOT IN (
            'BRASIL E UNIDADES DA FEDERAÇÃO',
            'Fonte: IBGE. Diretoria de Pesquisas - DPE -  Coordenação de População e Indicadores Sociais - COPIS.'
        )
        AND Field2 IS NOT NULL
    """)

    # Create cities table using Field1-Field5 as shown in test results
    df.execute(f"""
        CREATE OR REPLACE TABLE cities AS
        SELECT 
            Field1 as state_abbr,
            Field2 as state_code,
            Field3 as city_code,
            Field4 as city_name,
            CAST(Field5 AS BIGINT) as population
        FROM ST_read(
            '{excel_file_str}', 
            layer='MUNICÍPIOS',
            open_options=['HEADERS=FORCE']
        )
        WHERE Field1 NOT IN (
            'ESTIMATIVAS DA POPULAÇÃO RESIDENTE NOS MUNICÍPIOS BRASILEIROS COM DATA DE REFERÊNCIA EM 1º DE JULHO DE 2024',
            'UF'
        )
        AND Field1 IS NOT NULL
    """)

    result = {'brasil': {}, 'regions': {}, 'states': {}, 'cities': {}}

    # Get Brasil total
    brasil_pop = df.execute("SELECT population FROM states WHERE name = 'Brasil'").fetchone()[0]
    result['brasil']['total_population'] = brasil_pop

    # Get total number of cities
    total_cities = df.execute('SELECT COUNT(*) FROM cities').fetchone()[0]
    result['brasil']['total_cities'] = total_cities

    # Get regions with same logic
    regions_query = """
        SELECT name as region, population 
        FROM states 
        WHERE name IN ('Norte', 'Nordeste', 'Sudeste', 'Sul', 'Centro-Oeste')
    """
    regions = df.execute(regions_query).fetchall()
    for region, pop in regions:
        result['regions'][region.lower()] = {'total_population_per_region': pop}

    # State mapping remains the same
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
    abbr_to_state = {v: k for k, v in state_mapping.items()}

    # Process states first to get their populations
    state_populations = {}
    states_query = """
        SELECT name, population 
        FROM states 
        WHERE name NOT IN (
            'Brasil', 'Norte', 'Nordeste', 'Sudeste', 'Sul', 'Centro-Oeste'
        )
    """

    states = df.execute(states_query).fetchall()
    for state, pop in states:
        if state in state_mapping:
            # Get count of cities for this state
            state_abbr = state_mapping[state]
            cities_count = df.execute(f"SELECT COUNT(*) FROM cities WHERE state_abbr = '{state_abbr}'").fetchone()[0]

            result['states'][state] = {
                'state_abbr': state_abbr,
                'state_population': pop,
                'population_percentage': round(float(pop) / brasil_pop * 100, 2),
                'total_cities_this_state': cities_count,
            }
            state_populations[state_mapping[state]] = pop

    # Modified cities processing to use composite key
    cities_query = """
        SELECT 
            state_abbr,
            state_code,
            city_code,
            city_name,
            population
        FROM cities
        ORDER BY state_abbr, city_name
    """

    cities = df.execute(cities_query).fetchall()
    for state_abbr, state_code, city_code, city_name, pop in cities:
        if state_abbr in abbr_to_state:
            state_pop = state_populations[state_abbr]
            # Create a composite key using city name and state
            city_key = f'{city_name}_{state_abbr}'
            result['cities'][city_key] = {
                'city_name': city_name,
                'city_uf': state_abbr,
                'uf_code': state_code,
                'city_code': str(city_code).zfill(5),
                'city_population': pop,
                'population_percentage_total': round(float(pop) / brasil_pop * 100, 4),
                'population_percentage_state': round(float(pop) / state_pop * 100, 4),
            }

    # Save to JSON with proper encoding
    with Path('population_data_2024_review.json').open('w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return result


if __name__ == '__main__':
    try:
        data = create_population_dict()
    except Exception as e:
        print(f'An error occurred during population data extraction: {e}')
