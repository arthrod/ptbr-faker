import json
import csv
from math import isclose

def load_json_data():
    with open('common_names.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_csv_data():
    csv_data = {}
    with open('nomes-censos-percentages.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Nome'] == 'TOTALS':
                continue
            name = row['Nome']
            proportions = {}
            for period in row.keys():
                if period != 'Nome':
                    value = row[period]
                    proportions[period] = float(value) if value else 0
            csv_data[name] = proportions
    return csv_data

def values_match(v1, v2, rel_tol=1e-9, abs_tol=1e-9):
    if v1 == 0 and v2 == 0:
        return True
    return isclose(v1, v2, rel_tol=rel_tol, abs_tol=abs_tol)

def compare_proportions():
    json_data = load_json_data()
    csv_data = load_csv_data()
    
    with open('results_names.txt', 'w', encoding='utf-8') as f:
        f.write("Comparing proportions between common_names.json and nomes-censos-percentages.csv\n")
        f.write("=" * 80 + "\n\n")
        
        # Check for names in both files
        all_names = sorted(set(json_data.keys()) | set(csv_data.keys()))
        
        for name in all_names:
            if name not in json_data:
                f.write(f"Name {name} found in CSV but missing in JSON\n")
                continue
            if name not in csv_data:
                f.write(f"Name {name} found in JSON but missing in CSV\n")
                continue
            
            json_props = json_data[name]['proportion']
            csv_props = csv_data[name]
            
            has_differences = False
            f.write(f"Results for {name}:\n")
            
            for period in json_props:
                json_value = json_props[period]
                csv_value = csv_props[period]
                
                matches = values_match(json_value, csv_value)
                if not matches:
                    has_differences = True
                    f.write(f"  {period}: ❌ NO MATCH - JSON={json_value:.9f}, CSV={csv_value:.9f}\n")
                else:
                    f.write(f"  {period}: ✓ MATCH ({json_value:.9f})\n")
            
            if has_differences:
                f.write("  WARNING: Some values don't match substantially!\n")
            else:
                f.write("  All values match substantially!\n")
            f.write("\n")

if __name__ == '__main__':
    compare_proportions()
