import json
from decimal import Decimal, getcontext
from pathlib import Path

import duckdb

# Set maximum precision for our calculations
getcontext().prec = 50


def calculate_percentage(value: int, total: int) -> Decimal:
    """
    Calculate percentage with maximum precision, never returning absolute zero.

    Args:
        value: The count for a specific name and period
        total: The total count for that period

    Returns:
        Decimal: The calculated percentage with maximum precision
    """
    if total == 0 or value == 0:
        return Decimal('0.000000000000000000001')  # Extremely small but non-zero

    # Convert to Decimal with maximum precision and calculate
    dec_value = Decimal(str(value))
    dec_total = Decimal(str(total))
    return dec_value / dec_total


def process_population_data(json_file: str, csv_file: str) -> None:
    """
    Process population data from CSV and update JSON file with both name-centric
    and period-centric percentage structures.

    Args:
        json_file: Path to the population JSON file
        csv_file: Path to the IBGE census names CSV file
    """
    try:
        # Initialize DuckDB connection
        con = duckdb.connect(':memory:')

        # Create names table
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

        # Load CSV data
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

        # Get all data at once
        data_sql = """
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
        all_data = con.execute(data_sql).fetchall()

        # Read JSON file
        with Path(json_file).open('r', encoding='utf-8') as f:
            population_data = json.load(f)

        # Initialize both data structures
        common_names = {}  # For name-centric structure
        common_names_percentage = {}  # For period-centric structure

        # Initialize period-centric structure
        for year in range(1930, 2020, 10):
            common_names_percentage[f'ate{year}'] = {'total': 0, 'names': {}}

        # Calculate totals first
        period_totals = {year: 0 for year in range(1930, 2020, 10)}

        # First pass: calculate totals
        for row in all_data:
            for idx, year in enumerate(range(1930, 2020, 10)):
                value = int(row[idx + 1])
                period_totals[year] += value
                common_names_percentage[f'ate{year}']['total'] = period_totals[year]

        # Add totals to name-centric structure
        for year, total in period_totals.items():
            common_names[f'total_ate{year}'] = total

        # Second pass: process each name for both structures
        for row in all_data:
            name = row[0]
            name_data = {}  # For name-centric structure

            # Process each period for this name
            for idx, year in enumerate(range(1930, 2020, 10)):
                value = int(row[idx + 1])
                period = f'ate{year}'

                # Calculate percentage
                percentage = calculate_percentage(value, period_totals[year])
                percentage_float = float(percentage)

                # Update name-centric structure
                name_data[period] = value
                name_data[f'appr_percentage_{period}'] = percentage_float

                # Update period-centric structure
                if value > 0:  # Only include names that actually existed in that period
                    common_names_percentage[period]['names'][name] = {'total': value, 'percentage': percentage_float}

            # Add to name-centric structure
            common_names[name] = name_data

        # Update the JSON data with both structures
        population_data['common_names'] = common_names
        population_data['common_names_percentage'] = common_names_percentage

        # Write back to JSON
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
