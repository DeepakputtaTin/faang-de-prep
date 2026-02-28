import pandas as pd
import json

file_path = 'FAANG_DE_Prep_v3.xlsx'
xl = pd.ExcelFile(file_path)

data = {}
for sheet_name in xl.sheet_names:
    df = xl.parse(sheet_name)
    
    # Drop rows/cols that are completely NA
    df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
    
    # Convert dataframe to dict, handling NaNs
    sheet_data = df.to_dict(orient='records')
    
    # Store in our main dictionary
    data[sheet_name] = sheet_data

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, default=str)

print("Data successfully extracted to data.json")
