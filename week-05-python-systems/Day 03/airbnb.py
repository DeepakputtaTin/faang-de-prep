import csv
import json

with open('airbnb.csv', newline='') as csvfile:
    csvreader = csv.DictReader(csvfile, delimiter=',')
    with open('airbnddata.json', 'w', encoding='utf-8') as jsonfile:
        for row in csvreader:
            if row['status'] == 'confirmed':
                amount_usd = 0.00
                if row['currency'] == 'USD':
                    amount_usd = float(row['amount']) * 1.00
                elif row['currency'] == 'EUR':
                    amount_usd = float(row['amount']) * 1.08
                elif row['currency'] == 'GBP':
                    amount_usd = float(row['amount']) * 1.27

                output = {
                    'booking_id': row['booking_id'],
                    'user_id': row['user_id'],
                    'property_id': row['property_id'],
                    'amount_usd': amount_usd
                }
                json_str = json.dumps(output)
                jsonfile.write(json_str + '\n')