import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

# File paths
POPULATION_DATA_PATH = Path(
    '/Users/arthrod/Library/CloudStorage/GoogleDrive-arthursrodrigues@gmail.com/My Drive/acode/atemp-drive/ptbr-faker/data/fixing_cities/population_data_2024_complete_revised.json'
)
CEP_DATA_PATH = Path(
    '/Users/arthrod/Library/CloudStorage/GoogleDrive-arthursrodrigues@gmail.com/My Drive/acode/atemp-drive/ptbr-faker/state_data/bq-results-20250130-084843-1738227134360.json'
)
OUTPUT_PATH = Path(
    '/Users/arthrod/Library/CloudStorage/GoogleDrive-arthursrodrigues@gmail.com/My Drive/acode/atemp-drive/ptbr-faker/data/fixing_cities/cities_with_ceps.jsonl'
)
MISMATCH_PATH = Path(
    '/Users/arthrod/Library/CloudStorage/GoogleDrive-arthursrodrigues@gmail.com/My Drive/acode/atemp-drive/ptbr-faker/data/fixing_cities/cep_mismatches.json'
)
MISSING_CITIES_PATH = Path(
    '/Users/arthrod/Library/CloudStorage/GoogleDrive-arthursrodrigues@gmail.com/My Drive/acode/atemp-drive/ptbr-faker/data/fixing_cities/missing_cities.json'
)

# Name mappings (BQ name -> Population Data name)
NAME_MAPPINGS = {
    'Florinia': 'Florínea',
    'Olhodagua do Borges': "Olho d'Água do Borges",
    'Grao Para': 'Grão-Pará',
    'Santa Isabel do Para': 'Santa Izabel do Pará',
    'Itapage': 'Dona Euzébia',
    'Biritibamirim': 'Biritiba Mirim',
    'Iguaraci': 'Iguaracy',
    'São Thome das Letras': 'São Tomé das Letras',
    'Passavinte': 'Passa Vinte',
    'Amparo de São Francisco': 'Amparo do São Francisco',
    'Muquem de São Francisco': 'Muquém do São Francisco',
    'Boa Saude': 'Januário Cicco',
    'Fortaleza do Tabocao': 'Tabocão',
    'Poxoreo': 'Poxoréu',
}


def normalize_name_for_matching(name):
    """
    Normalize a name for matching purposes (not for display).
    This removes accents, special chars, and converts to uppercase for comparison.
    """
    if not name:
        return ''

    # Remove accents and convert to uppercase
    name = ''.join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')
    name = name.upper()

    # Remove special characters and standardize spaces
    name = re.sub(r'[^A-Z0-9\s]', '', name)
    name = ' '.join(name.split())

    return name


def process_cep_range(start_cep, end_cep):
    """Process CEP range, handling None values."""
    if not start_cep or not end_cep:
        return '00000000', '99999999'
    return start_cep.replace('-', ''), end_cep.replace('-', '')


def is_cep_in_range(cep, start_cep, end_cep):
    """Check if CEP is within range."""
    return start_cep <= cep <= end_cep


def load_population_data():
    """Load population data with detailed logging of the structure."""
    print('Loading population data...', file=sys.stderr)

    log_file = open('logging.txt', 'w', encoding='utf-8')

    def log(msg):
        print(msg, file=log_file, flush=True)
        print(msg, file=sys.stderr)

    try:
        with open(POPULATION_DATA_PATH, encoding='utf-8') as f:
            data = json.load(f)

        log('\n=== Population Data Structure Analysis ===')
        log(f'Top level keys: {list(data.keys())}')

        # Log sample of first city to understand structure
        sample_city_key = next(iter(data['cities']))
        log(f'\nSample city key format: {sample_city_key}')
        log('Sample city data:')
        log(json.dumps(data['cities'][sample_city_key], indent=2))

        # Validate city keys format
        log('\n=== Analyzing City Keys ===')
        problematic_keys = []
        for key in list(data['cities'].keys())[:5]:
            city_data = data['cities'][key]
            expected_key = f"{city_data.get('city_name')}_{city_data.get('city_uf')}"
            log(f'Key: {key}')
            log(f"City name: {city_data.get('city_name')}")
            log(f"City UF: {city_data.get('city_uf')}")
            log(f'Expected key: {expected_key}')
            if key != expected_key:
                problematic_keys.append((key, expected_key))

        if problematic_keys:
            log('\nProblematic keys found:')
            for actual, expected in problematic_keys:
                log(f'Actual: {actual} | Expected: {expected}')

        normalized_to_original = {}
        original_data = {'cities': {}}

        for key, city_data in data['cities'].items():
            # Extract city_name and city_uf directly from the key
            key_parts = key.rsplit('_', 1)
            if len(key_parts) != 2:
                log(f'Warning: Invalid key format: {key}')
                continue

            city_name, city_uf = key_parts

            # Create normalized version for matching
            norm_name = normalize_name_for_matching(city_name)
            norm_key = f'{norm_name}_{city_uf}'

            # Store the data with all original fields
            city_entry = {
                'city_name': city_name,
                'city_uf': city_uf,
                'uf_code': city_data.get('uf_code'),
                'city_code': city_data.get('city_code'),
                'city_population': city_data.get('city_population'),
                'population_percentage_total': city_data.get('population_percentage_total'),
                'population_percentage_state': city_data.get('population_percentage_state'),
                'ddd': city_data.get('ddd'),
                'cep_range_begins': city_data.get('cep_range_begins'),
                'cep_range_ends': city_data.get('cep_range_ends'),
                'cep_range_begins_two': city_data.get('cep_range_begins_two', ''),
                'cep_range_ends_two': city_data.get('cep_range_ends_two', ''),
                'aka': city_data.get('aka', ''),
            }

            normalized_to_original[norm_key] = (key, city_entry)
            original_data['cities'][key] = city_entry

        log('\n=== Summary ===')
        log(f"Total cities processed: {len(data['cities'])}")
        log(f'Normalized mappings created: {len(normalized_to_original)}')

        return normalized_to_original, original_data

    except Exception as e:
        log(f'Error loading population data: {e}')
        log(f'Error details: {e!s}')
        raise
    finally:
        log_file.close()


def process_bq_results(normalized_to_original, original_data):
    """Process BQ results and match with population data."""
    print('Processing BQ results...', file=sys.stderr)

    # Make a deep copy of original data to preserve ALL fields
    output_data = {'cities': {}}
    for city_key, city_data in original_data['cities'].items():
        output_data['cities'][city_key] = city_data.copy()  # Preserve ALL original fields
        output_data['cities'][city_key]['ceps'] = []  # Initialize as list, not set

    mismatches = defaultdict(lambda: {'in_range': [], 'out_of_range': [], 'wrong_uf': []})
    missing_cities = defaultdict(lambda: {'ceps': set(), 'ufs': set()})

    try:
        with open(CEP_DATA_PATH, encoding='utf-8') as f:
            for line_count, line in enumerate(f, 1):
                if line_count % 10000 == 0:
                    print(f'Processed {line_count} lines...', file=sys.stderr)

                data = json.loads(line.strip())
                city_name = data.get('nome_municipio')
                city_uf = data.get('sigla_uf')
                cep = data.get('cep', '').replace('-', '')  # Just normalize format

                if not all([city_name, city_uf, cep]):
                    continue

                mapped_name = NAME_MAPPINGS.get(city_name, city_name)
                norm_name = normalize_name_for_matching(mapped_name)
                norm_key = f'{norm_name}_{city_uf}'

                city_entry = normalized_to_original.get(norm_key)
                if city_entry is None:
                    missing_cities[city_name]['ceps'].add(cep)
                    missing_cities[city_name]['ufs'].add(city_uf)
                    continue

                original_key, _ = city_entry
                if cep not in output_data['cities'][original_key]['ceps']:
                    output_data['cities'][original_key]['ceps'].append(cep)

        # Sort the CEP lists
        for city_data in output_data['cities'].values():
            city_data['ceps'].sort()

        # Convert missing cities sets to sorted lists
        for city_data in missing_cities.values():
            city_data['ceps'] = sorted(list(city_data['ceps']))
            city_data['ufs'] = sorted(list(city_data['ufs']))

        return output_data, mismatches, missing_cities

    except Exception as e:
        print(f'Error processing BQ results: {e}', file=sys.stderr)
        raise


def ensure_output_directories():
    """Ensure all output directories exist."""
    print('Ensuring output directories exist...', file=sys.stderr)
    try:
        for path in [OUTPUT_PATH, MISMATCH_PATH, MISSING_CITIES_PATH]:
            path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f'Error creating directories: {e}', file=sys.stderr)
        raise


def write_output(output_data, mismatches, missing_cities):
    """Write output files maintaining original population data format."""
    print('Writing output files...', file=sys.stderr)
    try:
        # Write main output - output_data already has the correct structure with top-level "cities" key
        with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        # Write mismatches
        with open(MISMATCH_PATH, 'w', encoding='utf-8') as f:
            json.dump(mismatches, f, ensure_ascii=False, indent=2)

        # Write missing cities
        with open(MISSING_CITIES_PATH, 'w', encoding='utf-8') as f:
            json.dump(missing_cities, f, ensure_ascii=False, indent=2)

        print('Output files written successfully:', file=sys.stderr)
        print(f'- Main output: {OUTPUT_PATH}', file=sys.stderr)
        print(f'- Mismatches: {MISMATCH_PATH}', file=sys.stderr)
        print(f'- Missing cities: {MISSING_CITIES_PATH}', file=sys.stderr)

    except Exception as e:
        print(f'Error writing output files: {e}', file=sys.stderr)
        raise


def main():
    try:
        ensure_output_directories()
        normalized_to_original, original_data = load_population_data()
        output_data, mismatches, missing_cities = process_bq_results(normalized_to_original, original_data)
        write_output(output_data, mismatches, missing_cities)
    except Exception as e:
        print(f'Fatal error: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
