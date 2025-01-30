import json
from datetime import datetime

def load_common_names():
    with open('/Users/arthrod/Library/CloudStorage/GoogleDrive-arthursrodrigues@gmail.com/My Drive/acode/atemp-drive/ptbr-faker/data/names/old/common_names.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_population_data():
    with open('/Users/arthrod/Library/CloudStorage/GoogleDrive-arthursrodrigues@gmail.com/My Drive/acode/atemp-drive/ptbr-faker/data/population_data_2024_with_postalcodes_updated.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def update_population_data():
    common_names = load_common_names()
    population_data = load_population_data()
    
    # Prepare log file
    log_file = f'update_population_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    with open(log_file, 'w', encoding='utf-8') as log:
        log.write("Starting population data update\n")
        log.write("=" * 80 + "\n\n")
        
        # Update common_names section (appr_percentage fields)
        log.write("Updating common_names section (appr_percentage fields):\n")
        for name, data in common_names.items():
            if name in population_data['common_names']:
                old_data = population_data['common_names'][name]
                
                for period in ['ate1930', 'ate1940', 'ate1950', 'ate1960', 'ate1970', 'ate1980', 'ate1990', 'ate2000', 'ate2010']:
                    # Only update if the percentage field already exists
                    percentage_key = f'appr_percentage_{period}'
                    if percentage_key in old_data:
                        old_value = old_data[percentage_key]
                        new_value = data['proportion'][period]
                        old_data[percentage_key] = new_value
                        
                        if old_value != new_value:
                            log.write(f"  {name} - {percentage_key}: {old_value:.20e} -> {new_value:.20e}\n")
                            print(f"Updated {name} {percentage_key}")  # Debug print
            else:
                log.write(f"  WARNING: {name} not found in population data common_names section\n")
        
        # Update common_names_percentage section
        log.write("\nUpdating common_names_percentage section:\n")
        if 'common_names_percentage' in population_data:
            for name, data in common_names.items():
                if name in population_data['common_names_percentage']:
                    old_data = population_data['common_names_percentage'][name]
                    
                    for period in ['ate1930', 'ate1940', 'ate1950', 'ate1960', 'ate1970', 'ate1980', 'ate1990', 'ate2000', 'ate2010']:
                        if period in old_data:  # Only update existing periods
                            old_value = old_data[period]
                            new_value = data['proportion'][period]
                            old_data[period] = new_value
                            
                            if old_value != new_value:
                                log.write(f"  {name} - {period}: {old_value:.20e} -> {new_value:.20e}\n")
                                print(f"Updated {name} {period}")  # Debug print
                else:
                    log.write(f"  WARNING: {name} not found in population data common_names_percentage section\n")
        else:
            log.write("  ERROR: common_names_percentage section not found in population data\n")
    
    # Save updated population data
    with open('/Users/arthrod/Library/CloudStorage/GoogleDrive-arthursrodrigues@gmail.com/My Drive/acode/atemp-drive/ptbr-faker/data/population_data_2024_with_postalcodes_updated.json', 'w', encoding='utf-8') as f:
        json.dump(population_data, f, indent=2, ensure_ascii=False)
        
    print(f"Update completed. Check {log_file} for details.")

if __name__ == '__main__':
    update_population_data()
