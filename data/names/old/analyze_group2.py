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

def analyze_group2():
    common_names = load_common_names()
    population_data = load_population_data()
    
    periods = ['ate1930', 'ate1940', 'ate1950', 'ate1960', 'ate1970', 'ate1980', 'ate1990', 'ate2000', 'ate2010']
    
    # Track missing patterns
    missing_all_periods: Set[str] = set()
    missing_some_periods: Dict[str, List[str]] = defaultdict(list)
    present_periods: Dict[str, List[str]] = defaultdict(list)
    
    # Analyze each name
    for name in common_names.keys():
        missing_count = 0
        
        # Check each period
        for period in periods:
            period_data = population_data['common_names_percentage'].get(period, {})
            if 'names' not in period_data or name not in period_data['names']:
                missing_count += 1
                missing_some_periods[name].append(period)
            else:
                present_periods[name].append(period)
        
        # If missing from all periods, add to missing_all_periods
        if missing_count == len(periods):
            missing_all_periods.add(name)
            del missing_some_periods[name]  # Remove from missing_some_periods
    
    # Generate report
    log_file = f'group2_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    with open(log_file, 'w', encoding='utf-8') as log:
        log.write("Analysis of Group 2 (common_names_percentage)\n")
        log.write("=" * 80 + "\n\n")
        
        # Names missing from all periods
        log.write("Names missing from ALL periods:\n")
        log.write("-" * 40 + "\n")
        if missing_all_periods:
            for name in sorted(missing_all_periods):
                log.write(f"{name}\n")
        else:
            log.write("None\n")
        
        # Names missing from some periods
        log.write("\nNames missing from SOME periods:\n")
        log.write("-" * 40 + "\n")
        if missing_some_periods:
            for name in sorted(missing_some_periods.keys()):
                missing = missing_some_periods[name]
                present = present_periods[name]
                log.write(f"\n{name}:\n")
                log.write(f"  Missing in {len(missing)}/{len(periods)} periods: {', '.join(missing)}\n")
                log.write(f"  Present in {len(present)}/{len(periods)} periods: {', '.join(present)}\n")
        else:
            log.write("None\n")
        
        # Summary statistics
        total_names = len(common_names)
        missing_all = len(missing_all_periods)
        missing_some = len(missing_some_periods)
        fully_present = total_names - missing_all - missing_some
        
        log.write("\nSummary Statistics:\n")
        log.write("-" * 40 + "\n")
        log.write(f"Total names analyzed: {total_names}\n")
        log.write(f"Names missing from all periods: {missing_all} ({missing_all/total_names*100:.2f}%)\n")
        log.write(f"Names missing from some periods: {missing_some} ({missing_some/total_names*100:.2f}%)\n")
        log.write(f"Names present in all periods: {fully_present} ({fully_present/total_names*100:.2f}%)\n")
    
    print(f"Analysis completed. Check {log_file} for details.")

if __name__ == '__main__':
    analyze_group2()
