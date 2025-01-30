import json
from datetime import datetime
from typing import Dict, Set

def load_common_names() -> Dict:
    with open('/Users/arthrod/Library/CloudStorage/GoogleDrive-arthursrodrigues@gmail.com/My Drive/acode/atemp-drive/ptbr-faker/data/names/old/common_names.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_population_data() -> Dict:
    with open('/Users/arthrod/Library/CloudStorage/GoogleDrive-arthursrodrigues@gmail.com/My Drive/acode/atemp-drive/ptbr-faker/data/population_data_2024_with_postalcodes_updated.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def format_value(value):
    if isinstance(value, (int, float)):
        return f"{value:.20e}"
    return str(value)

def update_names():
    common_names = load_common_names()
    population_data = load_population_data()
    
    # Prepare log file
    log_file = f'update_names_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    
    # Keep track of names not found in each group
    names_not_in_group1 = set()
    names_not_in_group2 = set()
    
    with open(log_file, 'w', encoding='utf-8') as log:
        # Group 1: common_names section with name-based structure
        log.write("Group 1:\n")
        log.write("=" * 80 + "\n")
        
        for name, data in common_names.items():
            if name in population_data['common_names']:
                name_data = population_data['common_names'][name]
                for period in ['ate1930', 'ate1940', 'ate1950', 'ate1960', 'ate1970', 'ate1980', 'ate1990', 'ate2000', 'ate2010']:
                    if period in name_data and f'appr_percentage_{period}' in name_data:
                        old_value = name_data[f'appr_percentage_{period}']
                        new_value = data['proportion'][period]
                        if old_value != new_value:
                            log.write(f"name {name} found, value is different for {period}, substitute {format_value(old_value)} to {format_value(new_value)}\n")
                            name_data[f'appr_percentage_{period}'] = new_value
                        else:
                            log.write(f"name {name} found, value is correct for {period}: {format_value(old_value)}\n")
            else:
                log.write(f"name {name} not found\n")
                names_not_in_group1.add(name)
        
        log.write("\nConsolidated names not found in group 1:\n")
        for name in sorted(names_not_in_group1):
            log.write(f"{name}\n")
        
        # Group 2: common_names_percentage section with period-based structure
        log.write("\nGroup 2:\n")
        log.write("=" * 80 + "\n")
        
        if 'common_names_percentage' in population_data:
            for period in ['ate1930', 'ate1940', 'ate1950', 'ate1960', 'ate1970', 'ate1980', 'ate1990', 'ate2000', 'ate2010']:
                period_data = population_data['common_names_percentage'].get(period, {})
                if 'names' in period_data:
                    for name, data in common_names.items():
                        if name in period_data['names']:
                            old_value = period_data['names'][name]
                            new_value = data['proportion'][period]
                            if old_value != new_value:
                                log.write(f"name {name} found in {period}, value is different, substitute {format_value(old_value)} to {format_value(new_value)}\n")
                                period_data['names'][name] = new_value
                            else:
                                log.write(f"name {name} found in {period}, value is correct: {format_value(old_value)}\n")
                        else:
                            log.write(f"name {name} not found in {period}\n")
                            names_not_in_group2.add(f"{name} ({period})")
                    
                    # Update total
                    if 'total' in period_data:
                        new_total = sum(data['proportion'][period] for data in common_names.values())
                        if period_data['total'] != new_total:
                            log.write(f"total for {period} is different, substitute {format_value(period_data['total'])} to {format_value(new_total)}\n")
                            period_data['total'] = new_total
                        else:
                            log.write(f"total for {period} is correct: {format_value(period_data['total'])}\n")
        
        log.write("\nConsolidated names not found in group 2:\n")
        for name in sorted(names_not_in_group2):
            log.write(f"{name}\n")
    
    # Save updated population data
    with open('/Users/arthrod/Library/CloudStorage/GoogleDrive-arthursrodrigues@gmail.com/My Drive/acode/atemp-drive/ptbr-faker/data/population_data_2024_with_postalcodes_updated.json', 'w', encoding='utf-8') as f:
        json.dump(population_data, f, indent=2, ensure_ascii=False)
    
    print(f"Update completed. Check {log_file} for details.")

if __name__ == '__main__':
    update_names()
