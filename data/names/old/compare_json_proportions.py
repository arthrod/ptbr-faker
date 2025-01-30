import json
from math import isclose

def load_common_names():
    with open('common_names.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_population_data():
    with open('/Users/arthrod/Library/CloudStorage/GoogleDrive-arthursrodrigues@gmail.com/My Drive/acode/atemp-drive/ptbr-faker/data/population_data_2024_with_postalcodes_updated.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data['common_names']

def values_match(v1, v2):
    # Exact match for zero values
    if v1 == 0 and v2 == 0:
        return True
    # For non-zero values, require exact match
    return v1 == v2

def compare_proportions():
    common_names = load_common_names()
    population_data = load_population_data()
    
    # Remove total fields from population data
    total_fields = {k: v for k, v in population_data.items() if k.startswith('total_')}
    names_population = {k: v for k, v in population_data.items() if not k.startswith('total_')}
    
    with open('results_percentage.txt', 'w', encoding='utf-8') as f:
        f.write("Comparing proportions between common_names.json and population_data_2024_with_postalcodes_updated.json\n")
        f.write("=" * 100 + "\n\n")
        
        f.write("Population Data Totals:\n")
        for period, total in total_fields.items():
            f.write(f"  {period}: {total:,}\n")
        f.write("\n")
        
        # Check for names in both files
        all_names = sorted(set(common_names.keys()) | set(names_population.keys()))
        
        for name in all_names:
            if name not in common_names:
                f.write(f"Name {name} found in population data but missing in common_names.json\n")
                continue
            if name not in names_population:
                f.write(f"Name {name} found in common_names.json but missing in population data\n")
                continue
            
            common_props = common_names[name]['proportion']
            pop_props = names_population[name]
            
            has_differences = False
            f.write(f"Results for {name}:\n")
            
            for period in common_props:
                common_value = common_props[period]
                pop_value = pop_props[f'appr_percentage_{period}']
                
                # Always show the values
                f.write(f"  {period}:\n")
                f.write(f"    common_names: {common_value:.20e}\n")
                f.write(f"    population:   {pop_value:.20e}\n")
                
                if not values_match(common_value, pop_value):
                    has_differences = True
                    f.write("    ❌ DIFFERENT\n")
                else:
                    f.write("    ✓ MATCH\n")
            
            if has_differences:
                f.write("  WARNING: Values don't match!\n")
            else:
                f.write("  All values match!\n")
            f.write("\n")

if __name__ == '__main__':
    compare_proportions()
