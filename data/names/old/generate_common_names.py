import csv
import json
from collections import defaultdict

def process_names():
    names_data = {}
    period_totals = defaultdict(int)
    
    # First pass: calculate totals for each period
    with open('nomes-censos-ibge.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        periods = [col for col in reader.fieldnames if col != 'Nome']
        
        for row in reader:
            for period in periods:
                count = int(row[period]) if row[period] else 0
                period_totals[period] += count
    
    # Second pass: calculate proportions
    with open('nomes-censos-ibge.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            name = row['Nome']
            total = 0
            proportions = {}
            
            # Calculate total and proportions
            for period in periods:
                count = int(row[period]) if row[period] else 0
                total += count
                
                if count == 0:
                    proportions[period] = 0
                else:
                    # Calculate proportion against period total
                    proportions[period] = count / period_totals[period]
            
            names_data[name] = {
                "total": total,
                "proportion": proportions
            }
    
    # Write to JSON file
    with open('common_names.json', 'w', encoding='utf-8') as f:
        json.dump(names_data, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    process_names()
