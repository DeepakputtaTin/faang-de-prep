import json
data = json.load(open('clean_data.json'))
out = [{'w':d['Week'],'day':d['Day'],'topic':d.get('SpecificTopic',''),'theme':d.get('Theme',''),'action':d.get('ActionItem_Deliverable','')} for d in data]
with open('topics_map.json','w') as f:
    json.dump(out, f, indent=2)
print("done")
