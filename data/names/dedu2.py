import json

import pandas as pd


# 1. Read the JSONL file
def read_jsonl(file_path):
    names = []
    with open(file_path, encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            names.append(data['nome'])
    return names


# 2. Remove standalone first/second characters
def clean_standalone_chars(name):
    parts = name.split()
    while len(parts) > 1 and len(parts[0]) == 1:
        parts.pop(0)
    return ' '.join(parts)


# 3. Remove first names that match census data
def remove_census_first_names(names, census_file):
    census_df = pd.read_csv(census_file)
    census_first_names = set(census_df.iloc[:, 0].str.upper())

    cleaned_names = []
    for name in names:
        first_name = name.split()[0]
        if first_name not in census_first_names:
            cleaned_names.append(name)
    return cleaned_names


# 4. Extract last names considering Brazilian naming patterns
def extract_last_names(name):
    parts = name.split()
    if len(parts) <= 1:
        return name

    # Define connecting words (prepositions)
    connecting_words = {'DE', 'DA', 'DO', 'DOS', 'DAS', 'E'}

    last_names = []
    current_group = []

    # Process from right to left
    for part in reversed(parts):
        if len(current_group) == 0 or part.upper() in connecting_words or len(part) <= 3:
            current_group.insert(0, part)
        else:
            if current_group:
                last_names.insert(0, ' '.join(current_group))
                current_group = []
            current_group.insert(0, part)

    if current_group:
        last_names.insert(0, ' '.join(current_group))

    # Return last 3 family names
    return last_names[-3:]


# 5. Properly capitalize names and save unique ones
def capitalize_name(name):
    parts = name.split()
    capitalized_parts = []

    for part in parts:
        if len(part) <= 3 and part.upper() in {'DE', 'DA', 'DO', 'DOS', 'DAS', 'E'}:
            capitalized_parts.append(part.lower())
        else:
            capitalized_parts.append(part.capitalize())

    return ' '.join(capitalized_parts)


def main():
    # Read input file
    names = read_jsonl('names_mix_deduplicated.jsonl')

    # Clean standalone characters
    names = [clean_standalone_chars(name) for name in names]

    # Remove census first names
    names = remove_census_first_names(names, 'nomes-censos-ibge.csv')

    # Extract and process last names
    family_names = set()
    for name in names:
        last_names = extract_last_names(name)
        for last_name in last_names:
            family_names.add(capitalize_name(last_name))

    # Save to new JSONL file
    with open('family_names.jsonl', 'w', encoding='utf-8') as f:
        for family_name in sorted(family_names):
            json.dump({'nome': family_name}, f, ensure_ascii=False)
            f.write('\n')


if __name__ == '__main__':
    main()
