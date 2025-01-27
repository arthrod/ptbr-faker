import csv
import json


def read_jsonl(file_path):
    names = []
    with open(file_path, encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            names.append(data['nome'])  # Keep original case for writing back
    return names


def read_csv_names(file_path):
    names = set()
    with open(file_path, encoding='utf-8') as f:
        csv_reader = csv.reader(f)
        next(csv_reader)  # Skip header row
        for row in csv_reader:
            if row:  # Check if row is not empty
                names.add(row[0].lower())  # Convert to lowercase
    return names


def write_jsonl(file_path, names):
    with open(file_path, 'w', encoding='utf-8') as f:
        for name in names:
            json_line = json.dumps({'nome': name}, ensure_ascii=False)
            f.write(json_line + '\n')


def main():
    # Read original names
    family_names = read_jsonl('family_names_sorted.jsonl')
    initial_count = len(family_names)
    print(f'Initial count: {initial_count}')

    # Read and create lowercase sets for comparison
    top_40_names = read_csv_names('top_40.csv')
    censo_names = read_csv_names('nomes-censos-ibge.csv')

    # Filter names case-insensitively but keep original case in result
    family_names = [name for name in family_names if name.lower() not in top_40_names and name.lower() not in censo_names]

    # Write filtered results back to file
    write_jsonl('family_names_sorted.jsonl', family_names)

    final_count = len(family_names)
    print(f'Final count: {final_count}')
    print(f'Removed {initial_count - final_count} names')


if __name__ == '__main__':
    main()
