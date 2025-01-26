import json
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import duckdb


def process_population_data(json_file: str, csv_file: str) -> None:
    """
    Process population data from CSV and update JSON file with common names statistics using DuckDB.

    Args:
        json_file: Path to the population JSON file
        csv_file: Path to the IBGE census names CSV file
    """
    try:
        # Initialize DuckDB connection
        con = duckdb.connect(':memory:')

        # Create and populate the names table with proper schema
        create_table_sql = """
        CREATE TABLE names (
            Nome VARCHAR,
            ate1930 BIGINT,
            ate1940 BIGINT,
            ate1950 BIGINT,
            ate1960 BIGINT,
            ate1970 BIGINT,
            ate1980 BIGINT,
            ate1990 BIGINT,
            ate2000 BIGINT,
            ate2010 BIGINT
        );
        """
        con.execute(create_table_sql)

        # Load CSV data with proper handling of empty values
        copy_sql = f"""
        COPY names FROM '{csv_file}'
        WITH (
            HEADER TRUE,
            DELIMITER ',',
            FORCE_NOT_NULL (Nome),
            NULL ''
        );
        """
        con.execute(copy_sql)

        # Calculate totals for each period
        totals_sql = """
        SELECT 
            COALESCE(SUM(COALESCE(ate1930, 0)), 0) as total_ate1930,
            COALESCE(SUM(COALESCE(ate1940, 0)), 0) as total_ate1940,
            COALESCE(SUM(COALESCE(ate1950, 0)), 0) as total_ate1950,
            COALESCE(SUM(COALESCE(ate1960, 0)), 0) as total_ate1960,
            COALESCE(SUM(COALESCE(ate1970, 0)), 0) as total_ate1970,
            COALESCE(SUM(COALESCE(ate1980, 0)), 0) as total_ate1980,
            COALESCE(SUM(COALESCE(ate1990, 0)), 0) as total_ate1990,
            COALESCE(SUM(COALESCE(ate2000, 0)), 0) as total_ate2000,
            COALESCE(SUM(COALESCE(ate2010, 0)), 0) as total_ate2010
        FROM names;
        """
        totals = con.execute(totals_sql).fetchone()

        # Read the existing JSON file
        with Path(json_file).open('r', encoding='utf-8') as f:
            population_data = json.load(f)

        # Initialize common_names with totals
        common_names = {f'total_ate{year}': int(totals[i]) for i, year in enumerate(range(1930, 2020, 10))}

        # Process each name with its values and percentages
        names_sql = """
        SELECT 
            Nome,
            COALESCE(ate1930, 0) as ate1930,
            COALESCE(ate1940, 0) as ate1940,
            COALESCE(ate1950, 0) as ate1950,
            COALESCE(ate1960, 0) as ate1960,
            COALESCE(ate1970, 0) as ate1970,
            COALESCE(ate1980, 0) as ate1980,
            COALESCE(ate1990, 0) as ate1990,
            COALESCE(ate2000, 0) as ate2000,
            COALESCE(ate2010, 0) as ate2010
        FROM names
        ORDER BY Nome;
        """

        names_data = con.execute(names_sql).fetchall()

        # Process each name and calculate percentages
        for row in names_data:
            name = row[0]
            name_data = {}

            for i, year in enumerate(range(1930, 2020, 10)):
                value = int(row[i + 1])  # +1 because first column is Nome
                total = totals[i]

                # Calculate percentage with high precision
                if total > 0:
                    percentage = Decimal(value) / Decimal(total)
                    percentage = percentage.quantize(Decimal('0.00001'), rounding=ROUND_HALF_UP)
                else:
                    percentage = Decimal('0.00000')

                period = f'ate{year}'
                name_data[period] = value
                name_data[f'appr_percentage_{period}'] = float(percentage)

            common_names[name] = name_data

        # Update the JSON data
        population_data['common_names'] = common_names

        # Write back to JSON file with proper formatting
        with Path(json_file).open('w', encoding='utf-8') as f:
            json.dump(population_data, f, ensure_ascii=False, indent=2)

    except duckdb.Error as e:
        print(f'DuckDB Error: {e}')
    except FileNotFoundError as e:
        print(f'Error: Could not find file - {e}')
    except json.JSONDecodeError as e:
        print(f'Error: Invalid JSON format - {e}')
    except Exception as e:
        print(f'Unexpected error occurred: {e}')
    finally:
        if 'con' in locals():
            con.close()


if __name__ == '__main__':
    process_population_data('population_data_2024_with_postalcodes.json', 'nomes-censos-ibge.csv')
