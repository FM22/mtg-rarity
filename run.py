import json
import re
import unidecode

#read and parse the datafile
with open("data.json", encoding = "utf8") as f:
    data = json.load(f)

#parse oracle texts
orTxts = []
for card in data:
    orTxt = card["oracle_text"]
    orTxt = unidecode.unidecode(orTxt) #fix utf-8 (mostly en-dashes)
    orTxt = re.sub(card["name"], "CARDNAME", orTxt) #replace instances of self reference
    orTxt = re.sub(card["name"].split(" ")[0][:-1], "CARDNAME", orTxt) #replace self reference for legends of form "NAME, TITLE"
    orTxt = re.sub("\(.*\)", "", orTxt) #strip out reminder text (text in brackets)
    orTxt = re.sub("\n", " NEWLINE ", orTxt) #turn newlines into words
    orTxt = re.sub("\}\{", "} {", orTxt) #space out adjacent mana symbols
    orTxt = re.sub(":", " CCOLON ", orTxt) #turn colons into words
    orTxt = re.sub("\,|\.|--", "", orTxt) #remove all commas, full stops and dashes
    orTxt = re.sub("  ", " ", orTxt) #remove any generated double spaces
    orTxt = orTxt.lower() #make everything lowercase
    orTxts.append(orTxt)
    print(orTxt)
#print(orTxts)