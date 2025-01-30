import json
from datetime import datetime
from collections import defaultdict
from typing import Dict, Set, List

def load_common_names() -> Dict:
    with open('/Users/arthrod/Library/CloudStorage/GoogleDrive-arthursrodrigues@gmail.com/My Drive/acode/atemp-drive/ptbr-faker/data/names/old/common_names.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_population_data() -> Dict:
    with open('/Users/arthrod/Library/CloudStorage/GoogleDrive-arthursrodrigues@gmail.com/My Drive/acode/atemp-drive/ptbr-faker/data/population_data_2024_with_postalcodes_updated.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_missing_values():
    common_names = load_common_names()
    population_data = load_population_data()
    periods = ['ate1930', 'ate1940', 'ate1950', 'ate1960', 'ate1970', 'ate1980', 'ate1990', 'ate2000', 'ate2010']
    
    # Track different cases
    missing_with_zeros: Dict[str, List[str]] = defaultdict(list)
    missing_with_values: Dict[str, Dict[str, float]] = defaultdict(dict)
    
    # First, find missing names in group 2
    missing_in_periods: Dict[str, List[str]] = defaultdict(list)
    
    for name in common_names:
        for period in periods:
            period_data = population_data['common_names_percentage'].get(period, {})
            if 'names' not in period_data or name not in period_data['names']:
                missing_in_periods[name].append(period)
    
    # Analyze values in common_names.json for missing entries
    log_file = f'missing_values_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    with open(log_file, 'w', encoding='utf-8') as log:
        log.write("Analysis of Missing Names Values\n")
        log.write("=" * 80 + "\n\n")
        
        # Analyze each missing name
        for name, missing_periods in missing_in_periods.items():
            log.write(f"\nAnalyzing {name}:\n")
            log.write("-" * 40 + "\n")
            
            # Check values in common_names.json
            name_data = common_names[name]
            
            for period in missing_periods:
                value = name_data['proportion'][period]
                if value == 0:
                    missing_with_zeros[name].append(period)
                    log.write(f"  {period}: Missing in group 2 and IS zero in common_names.json\n")
                else:
                    missing_with_values[name][period] = value
                    log.write(f"  {period}: Missing in group 2 but has value {value:.20e} in common_names.json\n")
        
        # Summary statistics
        total_missing_periods = sum(len(periods) for periods in missing_in_periods.values())
        total_zero_periods = sum(len(periods) for periods in missing_with_zeros.values())
        total_value_periods = sum(len(periods) for periods in missing_with_values.values())
        
        log.write("\nSummary Statistics:\n")
        log.write("-" * 40 + "\n")
        log.write(f"Total missing period-name combinations: {total_missing_periods}\n")
        log.write(f"Missing entries with zero values: {total_zero_periods} ({total_zero_periods/total_missing_periods*100:.2f}%)\n")
        log.write(f"Missing entries with non-zero values: {total_value_periods} ({total_value_periods/total_missing_periods*100:.2f}%)\n")
        
        # Detailed lists
        log.write("\nNames missing with ALL zero values:\n")
        log.write("-" * 40 + "\n")
        for name, periods in missing_with_zeros.items():
            if len(periods) == len(missing_in_periods[name]):
                log.write(f"{name}: {', '.join(periods)}\n")
        
        log.write("\nNames missing with SOME non-zero values:\n")
        log.write("-" * 40 + "\n")
        for name in missing_with_values.keys():
            if name in missing_with_zeros:
                zero_periods = missing_with_zeros[name]
                value_periods = list(missing_with_values[name].keys())
                log.write(f"{name}:\n")
                log.write(f"  Zero in: {', '.join(zero_periods)}\n")
                log.write(f"  Non-zero in: {', '.join(value_periods)} ")
                log.write(f"(values: {', '.join(f'{period}={value:.20e}' for period, value in missing_with_values[name].items())})\n")
        
        log.write("\nNames missing with ALL non-zero values:\n")
        log.write("-" * 40 + "\n")
        for name, periods_values in missing_with_values.items():
            if name not in missing_with_zeros:
                log.write(f"{name}:\n")
                log.write(f"  Values: {', '.join(f'{period}={value:.20e}' for period, value in periods_values.items())}\n")
    
    print(f"Analysis completed. Check {log_file} for details.")

if __name__ == '__main__':
    analyze_missing_values()
