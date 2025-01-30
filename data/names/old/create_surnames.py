import csv
import json
from decimal import Decimal
from pathlib import Path
from typing import Any


class SurnameProcessor:
    def __init__(self, csv_path: Path, jsonl_path: Path):
        self.csv_path = csv_path
        self.jsonl_path = jsonl_path
        self.surnames: dict[str, dict[str, Decimal]] = {}
        self.other_names: set[str] = set()
        self.top40_total: Decimal = Decimal('0')

    def process_top40_csv(self) -> None:
        """
        Reads the top 40 CSV file and stores percentages with full precision.
        Each surname from top 40 gets stored with its original percentage.
        """
        with open(self.csv_path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                surname = row['surname']
                # Convert to Decimal for precise arithmetic
                percentage = Decimal(row['percentage'])
                self.surnames[surname] = {'original': percentage, 'normalized': Decimal('0'), 'top40': Decimal('0')}
                self.top40_total += percentage

    def process_other_names(self) -> None:
        """
        Reads the JSONL file containing other surnames.
        Each surname will get an equal share of the 30% allocation.
        """
        with open(self.jsonl_path, encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    self.other_names.add(entry['nome'])

    def calculate_percentages(self) -> None:
        """
        Calculates three different percentage values:
        1. Normalized percentages for top 40 (scaling to 70% total)
        2. Each top 40 surname's percentage within top 40 (scaling to 100%)
        3. Equal distribution of 30% among other surnames
        """
        # Constants as Decimal for precise calculation
        TOP40_TARGET = Decimal('70.0')
        OTHER_TARGET = Decimal('30.0')

        # Calculate scaling factor for top 40 names
        scale_factor = TOP40_TARGET / self.top40_total

        # Calculate percentage for other names
        other_count = Decimal(str(len(self.other_names)))
        per_other_name = OTHER_TARGET / other_count if other_count > 0 else Decimal('0')

        # Process top 40 surnames
        for data in self.surnames.values():
            orig = data['original']
            # Calculate 70% normalized percentage
            data['normalized'] = orig * scale_factor
            # Calculate 100% top 40 percentage
            data['top40'] = (orig / self.top40_total) * Decimal('100.0')

        # Add other surnames with their equal share of 30%
        for name in self.other_names:
            self.surnames[name] = {'original': per_other_name, 'normalized': per_other_name, 'top40': Decimal('0')}

    def generate_output(self) -> dict[str, Any]:
        """
        Generates the final output structure with precise percentages.
        Maintains full floating-point precision for all numbers.
        """
        output = {
            'surnames': {
                # Main surname listing
                **{surname: float(data['normalized']) for surname, data in self.surnames.items()},
                # Top 40 substructure
                'top_40': {
                    surname: {'percentage': float(data['top40'])}
                    for surname, data in self.surnames.items()
                    if data['original'] > 0 and 'top40' in data
                },
            }
        }
        return output

    def verify_totals(self) -> None:
        """
        Verifies that percentage totals are correct:
        - Main surnames sum to 100%
        - Top 40 percentages sum to 100%
        """
        total_main = sum(data['normalized'] for data in self.surnames.values())
        total_top40 = sum(data['top40'] for data in self.surnames.values() if data['original'] > 0)

        assert Decimal('99.9') < total_main < Decimal('100.1'), f'Main total incorrect: {total_main}'
        assert Decimal('99.9') < total_top40 < Decimal('100.1'), f'Top 40 total incorrect: {total_top40}'

    def process(self) -> dict[str, Any]:
        """
        Execute complete processing pipeline with verification
        """
        self.process_top40_csv()
        self.process_other_names()
        self.calculate_percentages()
        self.verify_totals()
        return self.generate_output()


def update_population_data(normalized_data: dict[str, Any], source_path: Path, output_path: Path) -> None:
    """
    Updates the population data file with new surname data
    """
    with open(source_path, encoding='utf-8') as f:
        population_data = json.load(f)

    # Update surnames while preserving file structure
    population_data['surnames'] = normalized_data['surnames']

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(population_data, f, indent=2, ensure_ascii=False)


def main():
    base_dir = Path(__file__).parent

    # Define input/output paths
    paths = {
        'top40': base_dir / 'top_40.csv',
        'family_names': base_dir / 'family_names_sorted.jsonl',
        'population_data': base_dir / 'population_data_2024_with_postalcodes.json',
        'output': base_dir / 'population_data_2024_with_postalcodes_updated.json',
    }

    try:
        processor = SurnameProcessor(paths['top40'], paths['family_names'])
        normalized_data = processor.process()

        update_population_data(normalized_data, paths['population_data'], paths['output'])

        print('Processing completed successfully')

    except Exception as e:
        print(f'Error during processing: {e!s}')
        raise


if __name__ == '__main__':
    main()
