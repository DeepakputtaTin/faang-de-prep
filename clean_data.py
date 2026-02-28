import json

with open('data.json', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

# Assuming the main data is in "Full 13-Week Plan" or similar
# Let's find the sheet and clean it
cleaned_data = []

for sheet_name, rows in raw_data.items():
    if not rows:
        continue
    
    # Extract keys from the first row that acts as a header
    header_row = rows[0]
    keys_map = {}
    for k, v in header_row.items():
        if isinstance(v, str):
            keys_map[k] = v.strip().replace(" / ", "_").replace(" ", "")
    
    # Process remaining rows
    sheet_cleaned = []
    for row in rows[1:]:
        clean_row = {}
        for old_k, old_v in row.items():
            if old_k in keys_map:
                new_k = keys_map[old_k]
                clean_row[new_k] = old_v if str(old_v) != 'nan' else None
        
        # Only add if it has a week and day
        if clean_row.get('Week') and clean_row.get('Day'):
            sheet_cleaned.append(clean_row)
            
    cleaned_data.extend(sheet_cleaned)

with open('clean_data.json', 'w', encoding='utf-8') as f:
    json.dump(cleaned_data, f, indent=4)

print("Cleaned data successfully.")
