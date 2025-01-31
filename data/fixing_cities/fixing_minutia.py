import json
import os

# Read the JSON file
file_path = '/Users/arthrod/Library/CloudStorage/GoogleDrive-arthursrodrigues@gmail.com/My Drive/acode/atemp-drive/ptbr-faker/data/fixing_cities/population_data_2024_complete_revised.json'

# Check if file exists
if not os.path.exists(file_path):
    print(f'Error: File not found at {file_path}')
    exit()

try:
    with open(file_path, encoding='utf-8') as f:
        data = json.load(f)
        print('Loaded data file')

    # Get the cities dictionary
    cities = data['cities']
    print(f'Found {len(cities)} cities')

    # Add counter to track changes
    changes_made = 0

    # Process only entries with comments
    for key, city_data in cities.items():
        if 'comment' in city_data:
            print(f'\nFound comment in: {key}')
            print(f'Comment value: {city_data["comment"]}')
            # Add aka field with just the city name part of the key
            city_name = key.split('_')[0]
            city_data['aka'] = city_name
            # Remove the comment field
            del city_data['comment']
            changes_made += 1

    print(f'\nTotal changes made: {changes_made}')

    if changes_made > 0:
        # Write back to the file with proper indentation
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print('File successfully updated!')
    else:
        print('No entries with comments found')

except Exception as e:
    print(f'An error occurred: {e!s}')
