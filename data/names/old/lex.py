# Read the file and process line by line
with open('lexicon.csv') as file:
    lines = file.readlines()

# Process header and data
header = lines[0].strip()  # First line is header
data = []
total = 0

# Process each data line
for line in lines[1:]:
    # Replace tab/spaces with comma and strip whitespace
    name, qty = line.strip().split('\t')
    qty = int(qty)
    total += qty
    data.append((name, qty))

# Calculate percentages and prepare output lines
output_lines = [f'{header},percentage\n']  # Add new header
for name, qty in data:
    percentage = (qty / total) * 100
    # Ensure percentage is never zero
    percentage = max(percentage, 0.0001)
    output_lines.append(f'{name},{qty},{percentage}\n')

# Write the processed data to new file
with open('lexicon_modified.csv', 'w') as file:
    file.writelines(output_lines)

print(f'Total sum: {total}')
print("File has been processed and saved as 'lexicon_modified.csv'")
