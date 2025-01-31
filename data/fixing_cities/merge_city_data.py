import csv
import json
from pathlib import Path

import jsonlines


def load_population_data():
    with open('population_data_2024_review.json', encoding='utf-8') as f:
        return json.load(f)


def parse_postal_ranges(postal_range_str):
    if not postal_range_str or postal_range_str == '[]':
        return None, None, None, None

    # Remove brackets and split if multiple ranges
    ranges = postal_range_str.strip('[]').split('] [')

    # Parse first range
    first_range = ranges[0].split()
    range_begins = first_range[0]
    range_ends = first_range[1]

    # Parse second range if exists
    range_begins_two = None
    range_ends_two = None
    if len(ranges) > 1:
        second_range = ranges[1].split()
        range_begins_two = second_range[0]
        range_ends_two = second_range[1]

    return range_begins, range_ends, range_begins_two, range_ends_two


def normalize_city_name(name, state):
    # Create a key similar to population data
    return f'{name}_{state}'


def merge_city_data():
    population_data = load_population_data()
    cities_in_pop_data = set(population_data['cities'].keys())
    cities_in_codes = set()

    # Prepare files for missing cities
    missing_cities_file = Path('missing_cities.jsonl')

    with jsonlines.open(missing_cities_file, mode='w') as writer:
        # Read and process br-city-codes.csv
        with open('br-city-codes.csv', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                city_name = row['name']
                state = row['state']
                city_key = normalize_city_name(city_name, state)
                cities_in_codes.add(city_key)

                # Parse postal ranges and DDD
                range_begins, range_ends, range_begins_two, range_ends_two = parse_postal_ranges(row['postalCode_ranges'])
                ddd = row['ddd'].zfill(2) if row['ddd'] else None

                if city_key in population_data['cities']:
                    # Update existing city data
                    city_data = population_data['cities'][city_key]
                    city_data.update(
                        {
                            'ddd': ddd,
                            'cep_range_begins': range_begins,
                            'cep_range_ends': range_ends,
                        }
                    )

                    if range_begins_two and range_ends_two:
                        city_data.update(
                            {
                                'cep_range_begins_two': range_begins_two,
                                'cep_range_ends_two': range_ends_two,
                            }
                        )
                else:
                    # Save missing city from codes
                    writer.write(
                        {
                            'source': 'br-city-codes',
                            'city_name': city_name,
                            'state': state,
                            'ddd': ddd,
                            'cep_range_begins': range_begins,
                            'cep_range_ends': range_ends,
                            'cep_range_begins_two': range_begins_two,
                            'cep_range_ends_two': range_ends_two,
                            'ibge_code': row['idIBGE'],
                        }
                    )

        # Find cities in population data but missing in codes
        missing_in_codes = cities_in_pop_data - cities_in_codes
        for city_key in missing_in_codes:
            city_data = population_data['cities'][city_key]
            writer.write(
                {
                    'source': 'population_data',
                    'city_name': city_data['city_name'],
                    'state': city_data['city_uf'],
                    'population': city_data['city_population'],
                    'city_code': city_data['city_code'],
                }
            )

    # Save updated population data
    with open('population_data_2024_complete.json', 'w', encoding='utf-8') as f:
        json.dump(population_data, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    try:
        merge_city_data()
        print('City data merge completed successfully')
    except Exception as e:
        print(f'An error occurred during city data merge: {e}')
