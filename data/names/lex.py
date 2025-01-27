import pandas as pd

# Read the CSV file with headers
df = pd.read_csv('lexicon.csv')

# Get the column names from the first row
name_col = df.columns[0]

# If data is in a single column, split it
if len(df.columns) == 1:
    # Split the single column into name and number
    df[['name', 'count']] = df[name_col].str.split('\t', expand=True)

    # Drop the original column
    df = df.drop(columns=[name_col])

    # Convert count to numeric
    df['count'] = pd.to_numeric(df['count'])

    # Calculate total sum
    total_sum = df['count'].sum()

    # Calculate percentage
    df['percentage'] = (df['count'] / total_sum) * 100

    # Ensure percentage is never rounded to zero
    df['percentage'] = df['percentage'].apply(lambda x: max(x, 0.0001))

    # Save to new CSV file
    df.to_csv('lexicon_modified.csv', index=False)

    print(f'Total sum: {total_sum}')
    print("File has been processed and saved as 'lexicon_modified.csv'")
else:
    print('CSV format is different than expected. Please check the file structure.')
