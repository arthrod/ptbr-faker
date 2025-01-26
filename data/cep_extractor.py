import json
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass
class ProcessingStats:
    """Class for tracking processing statistics"""

    total_cities: int = 0
    cities_updated: int = 0
    cities_without_postal_codes: list[dict[str, str]] = None
    postal_codes_not_found: list[dict[str, str]] = None

    def __post_init__(self):
        self.cities_without_postal_codes = []
        self.postal_codes_not_found = []


class PostalCodeProcessor:
    """Class for processing and integrating postal codes into population data"""

    def __init__(self, json_path: str, csv_path: str):
        """
        Initialize the processor with file paths

        Args:
            json_path: Path to the population JSON file
            csv_path: Path to the postal codes CSV file
        """
        self.json_path = Path(json_path)
        self.csv_path = Path(csv_path)
        self.stats = ProcessingStats()

    @staticmethod
    def normalize_string(text: str) -> str:
        """
        Normalize string by removing diacritics and converting to lowercase

        Args:
            text: Input string to normalize

        Returns:
            Normalized string
        """
        # Normalize unicode characters
        normalized = unicodedata.normalize('NFD', text)
        # Remove diacritics
        normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
        # Convert to lowercase and trim
        return normalized.lower().strip()

    @staticmethod
    def parse_postal_code_range(range_str: str) -> dict[str, str] | None:
        """
        Parse postal code range from string format

        Args:
            range_str: String containing postal code range in format [start-end]

        Returns:
            Dictionary with start and end postal codes, or None if invalid
        """
        if not range_str or range_str == '[]':
            return None

        # Remove brackets and split by comma (taking first range if multiple)
        range_clean = range_str.strip('[]').split(',')[0]
        if not range_clean:
            return None

        # Extract start and end postal codes
        try:
            start, end = range_clean.split(' ')
            return {'cep_starts': start.strip(), 'cep_ends': end.strip()}
        except ValueError:
            return None

    def read_files(self) -> tuple[dict[str, Any], pd.DataFrame]:
        """
        Read and parse both input files

        Returns:
            Tuple of (population data dict, postal codes DataFrame)
        """
        print(f'Reading population data from {self.json_path}...')
        with open(self.json_path, encoding='utf-8') as f:
            population_data = json.load(f)

        print(f'Reading postal codes from {self.csv_path}...')
        postal_codes_df = pd.read_csv(self.csv_path)

        return population_data, postal_codes_df

    def create_postal_code_lookup(self, df: pd.DataFrame) -> dict[str, str]:
        """
        Create a lookup dictionary from postal codes DataFrame

        Args:
            df: Postal codes DataFrame

        Returns:
            Dictionary mapping normalized city names to postal code ranges
        """
        return {self.normalize_string(row['name']): row['postalCode_ranges'] for _, row in df.iterrows()}

    def process_files(self) -> dict[str, Any]:
        """
        Main processing function to integrate postal codes into population data

        Returns:
            Dictionary containing processing results and statistics
        """
        try:
            # Read input files
            population_data, postal_codes_df = self.read_files()

            # Create lookup dictionary
            postal_code_lookup = self.create_postal_code_lookup(postal_codes_df)

            # Process each city
            for city_name, city_data in population_data['cities'].items():
                self.stats.total_cities += 1
                normalized_name = self.normalize_string(city_name)

                postal_code_range = postal_code_lookup.get(normalized_name)
                if postal_code_range:
                    parsed_range = self.parse_postal_code_range(postal_code_range)
                    if parsed_range:
                        # Update city data with postal codes
                        city_data.update(parsed_range)
                        self.stats.cities_updated += 1
                    else:
                        self.stats.cities_without_postal_codes.append(
                            {'city': city_name, 'state': city_data['city_uf'], 'reason': 'Invalid postal code format'}
                        )
                else:
                    self.stats.postal_codes_not_found.append({'city': city_name, 'state': city_data['city_uf']})

            # Generate output path
            output_path = self.json_path.with_name(self.json_path.stem + '_with_postalcodes.json')

            # Write updated data
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(population_data, f, indent=2, ensure_ascii=False)

            # Print processing report
            self._print_report()

            return {'success': True, 'stats': self.stats.__dict__, 'output_path': str(output_path)}

        except Exception as e:
            print(f'Error processing files: {e!s}')
            return {'success': False, 'error': str(e)}

    def _print_report(self):
        """Print detailed processing report"""
        print('\nProcessing Complete!')
        print('===================')
        print(f'Total cities processed: {self.stats.total_cities}')
        print(f'Cities updated with postal codes: {self.stats.cities_updated}')
        print(f'Cities without postal codes: {len(self.stats.postal_codes_not_found)}')

        if self.stats.postal_codes_not_found:
            print('\nCities without matching postal codes:')
            for city in self.stats.postal_codes_not_found:
                print(f"- {city['city']} ({city['state']})")

        if self.stats.cities_without_postal_codes:
            print('\nCities with invalid postal code format:')
            for city in self.stats.cities_without_postal_codes:
                print(f"- {city['city']} ({city['state']}): {city['reason']}")


def main():
    """Main entry point for the script"""
    # Initialize processor with file paths
    processor = PostalCodeProcessor(json_path='population_data_2024.json', csv_path='br-city-codes.csv')

    # Process files and get results
    result = processor.process_files()

    # Handle results
    if result['success']:
        print(f"\nUpdated data has been written to: {result['output_path']}")
    else:
        print(f"Processing failed: {result['error']}")
        exit(1)


if __name__ == '__main__':
    main()
