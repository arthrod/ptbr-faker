import json
from typing import Any, Dict
from datetime import datetime

def analyze_structure(data: Any, current_level: int = 0, max_level: int = 3) -> Dict:
    if current_level >= max_level:
        return "..."
    
    if isinstance(data, dict):
        return {k: analyze_structure(v, current_level + 1, max_level) for k, v in data.items()}
    elif isinstance(data, list):
        if len(data) > 0:
            return [analyze_structure(data[0], current_level + 1, max_level), f"... ({len(data)} items)"]
        return []
    else:
        return type(data).__name__

def extract_metadata():
    input_file = '/Users/arthrod/Library/CloudStorage/GoogleDrive-arthursrodrigues@gmail.com/My Drive/acode/atemp-drive/ptbr-faker/data/population_data_2024_with_postalcodes_updated.json'
    output_file = f'metadata_structure_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    print(f"Loading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("Analyzing structure...")
    structure = analyze_structure(data)
    
    print(f"Saving structure to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(structure, f, indent=2, ensure_ascii=False)
    
    print("\nStructure preview:")
    print(json.dumps(structure, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    extract_metadata()
