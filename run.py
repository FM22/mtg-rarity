import json

#read and parse the datafile
with open("data.json", encoding="utf8") as f:
    raw = f.read()
    data = json.loads(raw)

for card in data:
    if("Creature" in card["type_line"].split(" ") and card["layout"] == "normal"):
        i += 1
    j += 1
print(i)
print(j)
