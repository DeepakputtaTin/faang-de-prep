import csv
import json

data = {}
with open('test1.csv', newline='') as csvfile:
    csvreader = csv.DictReader(csvfile, delimiter=',')
    with open('test.json', 'w', encoding='utf-8') as jsonfile:
        for row in csvreader:
            json_str = json.dumps(row)
            jsonfile.write(json_str + '\n')



