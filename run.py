import json
import re

#read and parse the datafile
with open("data.json", encoding="utf8") as f:
    raw = f.read()
    data = json.loads(raw)

#parse oracle texts
orTxts = []
for card in data:
    orTxt = card["oracle_text"]
    orTxt = re.sub("\(.*\)", "", orTxt) #strip out reminder text (text in brackets)
    orTxt = re.sub("\n", " NEWLINE ", orTxt) #turn newlines into words
    orTxt = re.sub("\}\{", "} {", orTxt) #space out adjacent mana symbols
    orTxt = re.sub(":", " CCOLON ", orTxt) #turn colons into words
    orTxt = re.sub("  ", " ", orTxt) #remove any generated double spaces
    orTxt = re.sub("\,|\.", "", orTxt) #remove all commas and full stops
    orTxt = re.sub(card["name"], "CARDNAME", orTxt) #replace instances of self reference
    orTxt = orTxt.lower() #make everything lowercase
    print(orTxt)