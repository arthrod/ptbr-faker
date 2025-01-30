import csv
from collections import defaultdict

def generate_percentages():
    # First pass: calculate totals for each period
    period_totals = defaultdict(int)
    names_data = []
    
    with open('nomes-censos-ibge.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        periods = [col for col in reader.fieldnames if col != 'Nome']
        
        for row in reader:
            names_data.append(row)
            for period in periods:
                count = int(row[period]) if row[period] else 0
                period_totals[period] += count
    
    # Write the output CSV with percentages
    with open('nomes-censos-percentages.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        
        # Write header
        writer.writerow(['Nome'] + periods)
        
        # Write percentages for each name
        for row in names_data:
            name = row['Nome']
            percentages = []
            
            for period in periods:
                count = int(row[period]) if row[period] else 0
                if count == 0:
                    percentages.append('')
                else:
                    percentage = count / period_totals[period]
                    percentages.append(percentage)
            
            writer.writerow([name] + percentages)
        
        # Write totals row
        writer.writerow(['TOTALS'] + [1.0] * len(periods))

if __name__ == '__main__':
    generate_percentages()
