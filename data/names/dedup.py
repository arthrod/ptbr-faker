import json


def load_jsonl(file_path):
    data = []
    with open(file_path, encoding='utf-8') as f:
        for line in f:
            if line.strip():  # Skip empty lines
                data.append(json.loads(line))
    return data


def save_jsonl(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')


def main():
    # Load both files
    names_data = load_jsonl('names.jsonl')
    names_mix_data = load_jsonl('names_mix.jsonl')

    print(f'Original names.jsonl count: {len(names_data)}')
    print(f'Original names_mix.jsonl count: {len(names_mix_data)}')

    # Convert names.jsonl data to simple format and append to names_mix
    for item in names_data:
        names_mix_data.append({'nome': item['nome']})

    print(f'Combined count before deduplication: {len(names_mix_data)}')

    # Save combined data
    save_jsonl(names_mix_data, 'names_mix.jsonl')

    # Create deduplicated copy
    seen_names = set()
    deduplicated_data = []

    for item in names_mix_data:
        if item['nome'] not in seen_names:
            seen_names.add(item['nome'])
            deduplicated_data.append(item)

    # Save deduplicated data
    save_jsonl(deduplicated_data, 'names_mix_deduplicated.jsonl')

    print(f'Final count after deduplication: {len(deduplicated_data)}')


if __name__ == '__main__':
    main()
