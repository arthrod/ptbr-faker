import json
from pathlib import Path

import pandas as pd
import unidecode


def normalize_name(name):
    # Convert to title case and normalize accents for comparison
    name = name.title()
    return unidecode.unidecode(name)


def load_top_surnames():
    # Read and normalize top surnames
    top_df = pd.read_csv('top_40.csv')
    return {normalize_name(name) for name in top_df['surname']}


def process_middle_names():
    # Load existing consolidated names
    names_df = pd.read_csv('names_consolidated.csv')

    # Load top surnames to exclude
    top_surnames = load_top_surnames()

    # Dictionary to store middle name counts
    middle_names = {}
    total_count = 0

    # Process each full name
    for _, row in names_df.iterrows():
        full_name = row['Nome']
        count = row['total']

        # Split name into parts and process middle names
        name_parts = full_name.split()
        if len(name_parts) > 1:
            # Skip first name, process remaining parts
            for middle in name_parts[1:]:
                # Normalize for comparison
                normalized = normalize_name(middle)

                # Skip if in top surnames
                if normalized in top_surnames:
                    continue

                # Store original case version
                original = middle.title()
                if original not in middle_names:
                    middle_names[original] = 0
                middle_names[original] += count
                total_count += count

    # Calculate percentages and create final dict with proper structure
    middle_names_data = {name: {'percentage': (count / total_count) * 100} for name, count in middle_names.items()}

    # Sort by percentage descending
    middle_names_data = dict(sorted(middle_names_data.items(), key=lambda x: x[1]['percentage'], reverse=True))

    # Load existing JSON file
    json_path = Path('names_conso.json')
    if json_path.exists():
        with open(json_path, encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {}

    # Update with middle names
    data['middle_names'] = middle_names_data

    # Save back to JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f'Processed {len(middle_names)} unique middle names')
    print(f'Total middle name occurrences: {total_count:,}')


if __name__ == '__main__':
    process_middle_names()
