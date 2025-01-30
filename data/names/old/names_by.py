import glob

import pandas as pd


def process_names_data():
    # Find all relevant CSV files in current directory
    csv_files = glob.glob('names_by_state_*.csv')

    if not csv_files:
        print("Error: No CSV files found matching pattern 'names_by_state_*.csv'")
        return

    print(f'Found {len(csv_files)} files to process: {csv_files}')

    # Dictionary to store yearly dataframes
    yearly_data = {}

    # Process each file
    for file_path in csv_files:
        # Extract year from filename
        year = file_path.split('_')[-1].replace('.csv', '')

        # Read CSV
        df = pd.read_csv(file_path)

        # Calculate total for each name across all states
        state_columns = [col for col in df.columns if col != 'Nome']
        df['total_' + year] = df[state_columns].sum(axis=1)

        # Keep only Nome and total columns
        yearly_data[year] = df[['Nome', f'total_{year}']].copy()

    # Merge all yearly data on Nome
    result = yearly_data[list(yearly_data.keys())[0]]
    for year in list(yearly_data.keys())[1:]:
        result = result.merge(yearly_data[year], on='Nome', how='outer')

    # Calculate grand total across all years
    total_columns = [col for col in result.columns if col.startswith('total_')]
    result['total'] = result[total_columns].sum(axis=1, skipna=True)

    # Calculate total names across all years
    grand_total = result['total'].sum()

    # Calculate percentage
    result['percentage'] = (result['total'] / grand_total) * 100

    # Reorder columns
    # First get the years in descending order
    years = sorted([col.replace('total_', '') for col in total_columns], reverse=True)

    # Create final column order
    column_order = ['Nome', 'total', 'percentage'] + [f'total_{year}' for year in years]

    # Reorder columns and sort by total descending
    result = result[column_order].sort_values('total', ascending=False)

    # Fill NaN values with 0
    result = result.fillna(0)

    # Save to CSV
    result.to_csv('names_consolidated.csv', index=False)

    print(f'Processed {len(csv_files)} files')
    print(f'Total unique names: {len(result)}')
    print(f'Total occurrences: {grand_total:,.0f}')


if __name__ == '__main__':
    process_names_data()
