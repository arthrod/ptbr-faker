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
        self.top40_names: set[str] = set()

    def process_top40_csv(self) -> None:
        with open(self.csv_path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                surname = row['surname']
                percentage = Decimal(row['percentage'])
                self.surnames[surname] = {'original': percentage, 'normalized': Decimal('0'), 'top40': Decimal('0')}
                self.top40_total += percentage
                self.top40_names.add(surname)

    def process_other_names(self) -> None:
        with open(self.jsonl_path, encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    self.other_names.add(entry['nome'])

    def calculate_percentages(self) -> None:
        TOP40_TARGET = Decimal('70.0')
        OTHER_TARGET = Decimal('30.0')

        scale_factor = TOP40_TARGET / self.top40_total
        other_count = Decimal(str(len(self.other_names)))
        per_other_name = OTHER_TARGET / other_count if other_count > 0 else Decimal('0')

        # Process top 40 surnames
        for surname in self.top40_names:
            data = self.surnames[surname]
            orig = data['original']
            data['normalized'] = orig * scale_factor
            data['top40'] = (orig / self.top40_total) * Decimal('100.0')

        # Process other surnames
        for name in self.other_names:
            self.surnames[name] = {'original': per_other_name, 'normalized': per_other_name, 'top40': Decimal('0')}

    def generate_output(self) -> dict[str, Any]:
        """
        Fixed version with correct dictionary comprehension that properly references
        the surname data from self.surnames
        """
        output = {
            'surnames': {
                # Main surname listing with nested percentage objects
                **{surname: {'percentage': float(self.surnames[surname]['normalized'])} for surname, data in self.surnames.items()},
                # Top 40 substructure - accessing data through self.surnames
                'top_40': {surname: {'percentage': float(self.surnames[surname]['top40'])} for surname in self.top40_names},
            }
        }
        return output

    def verify_totals(self) -> None:
        total_main = sum(data['normalized'] for data in self.surnames.values())
        total_top40 = sum(self.surnames[name]['top40'] for name in self.top40_names)

        assert Decimal('99.9') < total_main < Decimal('100.1'), f'Main total incorrect: {total_main}'
        assert Decimal('99.9') < total_top40 < Decimal('100.1'), f'Top 40 total incorrect: {total_top40}'

    def process(self) -> dict[str, Any]:
        self.process_top40_csv()
        self.process_other_names()
        self.calculate_percentages()
        self.verify_totals()
        return self.generate_output()


def update_population_data(normalized_data: dict[str, Any], source_path: Path, output_path: Path) -> None:
    with open(source_path, encoding='utf-8') as f:
        population_data = json.load(f)

    population_data['surnames'] = normalized_data['surnames']

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(population_data, f, indent=2, ensure_ascii=False)


def main():
    base_dir = Path(__file__).parent

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
