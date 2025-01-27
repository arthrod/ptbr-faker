import json

# Read the JSONL file and store names in a list
names = []
with open('family_names.jsonl', encoding='utf-8') as file:
    for line in file:
        data = json.loads(line)
        names.append(data['nome'])

# Sort names by length
sorted_names = sorted(names, key=len)

# Write sorted names back to JSONL
with open('family_names_sorted.jsonl', 'w', encoding='utf-8') as file:
    for name in sorted_names:
        json_line = json.dumps({'nome': name}, ensure_ascii=False)
        file.write(json_line + '\n')

print('Names have been sorted by length and saved to family_names_sorted.jsonl')
