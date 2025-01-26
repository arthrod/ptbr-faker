from pathlib import Path

import duckdb


def explore_excel_spatial():
    """
    Comprehensive spatial and data analysis of the Excel file using DuckDB
    with extensive error handling and worksheet exploration.
    """
    df = duckdb.connect()

    print('\n=== PHASE 1: SPATIAL EXTENSION SETUP ===')
    try:
        df.execute("INSTALL 'spatial';")
        print('Spatial extension installed successfully')
    except Exception as e:
        print(f'Installation error: {e}')

    try:
        df.execute("LOAD 'spatial';")
        print('Spatial extension loaded successfully')
    except Exception as e:
        print(f'Loading error: {e}')

    excel_file_path = Path('estimativa_dou_2024.xlsx').resolve()
    excel_file_str = str(excel_file_path)

    print('\n=== PHASE 2: WORKSHEET DISCOVERY ===')

    # Method 1: Try direct layer listing
    print('\nMethod 1 - Direct layer listing:')
    try:
        layers = df.execute(f"""
            SELECT DISTINCT ST_GeometryType(geom) as layer_type
            FROM ST_read('{excel_file_str}')
        """).fetchall()
        print(f'Found layers: {layers}')
    except Exception as e:
        print(f'Method 1 error: {e}')

    # Method 2: Try with empty layer parameter
    print('\nMethod 2 - Empty layer parameter:')
    try:
        layers = df.execute(f"""
            SELECT *
            FROM ST_read(
                '{excel_file_str}',
                layer='',
                open_options=['LIST_ALL_TABLES=YES']
            )
        """).fetchall()
        print(f'Found layers: {layers}')
    except Exception as e:
        print(f'Method 2 error: {e}')

    # Method 3: Try specific worksheets
    print('\nMethod 3 - Known worksheet testing:')
    worksheets = ['BRASIL E UFs', 'MUNICÍPIOS']
    for sheet in worksheets:
        try:
            count = df.execute(f"""
                SELECT COUNT(*)
                FROM ST_read(
                    '{excel_file_str}',
                    layer='{sheet}',
                    open_options=['HEADERS=FORCE']
                )
            """).fetchone()[0]
            print(f"Worksheet '{sheet}' exists with {count} rows")
        except Exception as e:
            print(f"Error accessing worksheet '{sheet}': {e}")

    print('\n=== PHASE 3: DATA ANALYSIS ===')

    # Analyze BRASIL E UFs
    print('\nAnalyzing BRASIL E UFs sheet:')
    analysis_queries = [
        # Basic statistics
        """
        WITH state_data AS (
            SELECT 
                "ESTIMATIVAS DA POPULAÇÃO RESIDENTE NO BRASIL E UNIDADES DA FEDERAÇÃO COM DATA DE REFERÊNCIA EM 1º DE JULHO DE 2024" as name,
                CAST(Field2 AS BIGINT) as population
            FROM ST_read(
                '{file}',
                layer='BRASIL E UFs',
                open_options=['HEADERS=FORCE']
            )
            WHERE Field2 IS NOT NULL
        )
        SELECT 
            MIN(population) as min_pop,
            MAX(population) as max_pop,
            AVG(population) as avg_pop,
            COUNT(*) as total_entries
        FROM state_data
        """,
        # Population distribution
        """
        WITH state_data AS (
            SELECT 
                "ESTIMATIVAS DA POPULAÇÃO RESIDENTE NO BRASIL E UNIDADES DA FEDERAÇÃO COM DATA DE REFERÊNCIA EM 1º DE JULHO DE 2024" as name,
                CAST(Field2 AS BIGINT) as population
            FROM ST_read(
                '{file}',
                layer='BRASIL E UFs',
                open_options=['HEADERS=FORCE']
            )
            WHERE Field2 IS NOT NULL
            AND name NOT IN ('Brasil', 'Norte', 'Nordeste', 'Sudeste', 'Sul', 'Centro-Oeste')
        )
        SELECT 
            CASE 
                WHEN population < 1000000 THEN 'Less than 1M'
                WHEN population < 5000000 THEN '1M to 5M'
                WHEN population < 10000000 THEN '5M to 10M'
                ELSE 'More than 10M'
            END as pop_range,
            COUNT(*) as state_count
        FROM state_data
        GROUP BY pop_range
        ORDER BY state_count DESC
        """,
    ]

    for i, query in enumerate(analysis_queries, 1):
        print(f'\nAnalysis query {i}:')
        try:
            result = df.execute(query.format(file=excel_file_str)).fetchall()
            print(f'Result: {result}')
        except Exception as e:
            print(f'Query error: {e}')

    # Analyze MUNICÍPIOS
    print('\nAnalyzing MUNICÍPIOS sheet:')
    city_analysis_queries = [
        # Cities per state
        """
        SELECT 
            Field1 as state,
            COUNT(*) as city_count,
            SUM(CAST(Field5 AS BIGINT)) as total_population,
            AVG(CAST(Field5 AS BIGINT)) as avg_city_population
        FROM ST_read(
            '{file}',
            layer='MUNICÍPIOS',
            open_options=['HEADERS=FORCE']
        )
        WHERE Field1 NOT IN (
            'ESTIMATIVAS DA POPULAÇÃO RESIDENTE NOS MUNICÍPIOS BRASILEIROS COM DATA DE REFERÊNCIA EM 1º DE JULHO DE 2024',
            'UF'
        )
        GROUP BY Field1
        ORDER BY city_count DESC
        """,
        # Population distribution of cities
        """
        SELECT 
            CASE 
                WHEN CAST(Field5 AS BIGINT) < 10000 THEN 'Less than 10K'
                WHEN CAST(Field5 AS BIGINT) < 50000 THEN '10K to 50K'
                WHEN CAST(Field5 AS BIGINT) < 100000 THEN '50K to 100K'
                WHEN CAST(Field5 AS BIGINT) < 500000 THEN '100K to 500K'
                ELSE 'More than 500K'
            END as pop_range,
            COUNT(*) as city_count
        FROM ST_read(
            '{file}',
            layer='MUNICÍPIOS',
            open_options=['HEADERS=FORCE']
        )
        WHERE Field1 NOT IN (
            'ESTIMATIVAS DA POPULAÇÃO RESIDENTE NOS MUNICÍPIOS BRASILEIROS COM DATA DE REFERÊNCIA EM 1º DE JULHO DE 2024',
            'UF'
        )
        GROUP BY pop_range
        ORDER BY city_count DESC
        """,
    ]

    for i, query in enumerate(city_analysis_queries, 1):
        print(f'\nCity analysis query {i}:')
        try:
            result = df.execute(query.format(file=excel_file_str)).fetchall()
            print(f'Result: {result}')
        except Exception as e:
            print(f'Query error: {e}')

    print('\n=== PHASE 4: SPATIAL CAPABILITIES TESTING ===')

    try:
        spatial_queries = [
				# Test if geometry columns exist
				"""
			SELECT 
				column_name
			FROM ST_read(
				'{file}',
				layer='BRASIL E UFs',
				open_options=['HEADERS=FORCE']
			)
			WHERE column_name LIKE '%geom%' OR column_name LIKE '%geometry%'
			LIMIT 1
			""",
				# Test for spatial functions
				"""
			SELECT ST_GeometryType(geom)
			FROM ST_read(
				'{file}',
				layer='BRASIL E UFs',
				open_options=['HEADERS=FORCE']
			)
			WHERE geom IS NOT NULL
			LIMIT 1
			""",
			]
    except Exception as e:
        print(f'Error setting up spatial queries: {e}')
		pass

    for i, query in enumerate(spatial_queries, 1):
        print(f'\nSpatial query {i}:')
        try:
            result = df.execute(query.format(file=excel_file_str)).fetchall()
            print(f'Result: {result}')
        except Exception as e:
            print(f'Query error: {e}')

    return 'Exploration complete'


if __name__ == '__main__':
    try:
        explore_excel_spatial()
    except Exception as e:
        print(f'An error occurred during spatial exploration: {e}')
