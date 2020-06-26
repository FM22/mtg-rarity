import json
import re
import unidecode

#read and parse the datafile
with open("data.json", encoding = "utf8") as f:
    data = json.load(f)

ptDict = {"*": "0", "1+*": "1"} #converts */* creatures and Goyf

orTxts = []
powers = []
toughnesses = []
cmcs = []
xs = [0] * len(data)
gens = xs[:] #shallow copy
hybs = xs[:]
ws = xs[:]
us = xs[:]
rs = xs[:]
bs = xs[:]
gs = xs[:]
i = 0 #for loop counter
v = 0;
#extract data
for card in data:
    #parse oracle text
    orTxt = card["oracle_text"]
    orTxt = unidecode.unidecode(orTxt) #fix utf-8 (mostly en-dashes)
    orTxt = re.sub(card["name"], "CARDNAME", orTxt) #replace instances of self reference
    orTxt = re.sub(card["name"].split(" ")[0][:-1], "CARDNAME", orTxt) #replace self reference for legends of form "NAME, TITLE"
    orTxt = re.sub("\(.*\)", "", orTxt) #strip out reminder text (text in brackets)
    orTxt = re.sub("\n", " NEWLINE ", orTxt) #turn newlines into words
    orTxt = re.sub("\"", " QUOTE ", orTxt) #turn quote marks into words
    orTxt = re.sub("\}\{", "} {", orTxt) #space out adjacent mana symbols
    orTxt = re.sub(":", " COLON ", orTxt) #turn colons into words
    orTxt = re.sub("\,|\.|--|\*|;", " ", orTxt) #remove all commas, seimicolons, full stops, dashes (raid--, escape--, etc) and asterisks (choose one...)
    orTxt = re.sub("[ ]+", " ", orTxt) #remove any generated multiple spaces
    orTxt = re.sub("^ newline", "", orTxt) #remove leading newlines
    orTxt = re.sub("( $|^ )", "", orTxt) #remove leading and trailing spaces
    orTxt = orTxt.lower() #make everything lowercase
    orTxts.append(orTxt)
    if orTxt == "": v += 1

    #parse P/T
    powers.append(int(ptDict.get(card["power"], card["power"])))
    toughnesses.append(int(ptDict.get(card["toughness"], card["toughness"])))

    cmcs.append(card["cmc"]) #parse cmc

    #parse manacost
    for char in card["mana_cost"]:
        if char == "X": xs[i] += 1
        if char == "W": ws[i] += 1
        if char == "U": us[i] += 1
        if char == "B": bs[i] += 1
        if char == "R": rs[i] += 1
        if char == "G": gs[i] += 1
        if char == "/": hybs[i] += 1 #hybrid mana eg {W/U}
        if char in [str(i) for i in range(0,99)]: gens[i] += int(char) #generic mana
    i += 1


print(v)