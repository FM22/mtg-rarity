import json
import re
import unidecode

#read and parse the datafile
with open("data.json", encoding = "utf8") as f:
    data = json.load(f)

# list of input vectors
# index   value
# 0       power
# 1       toughness
# 2       cmc
# 3       X spell counter (non-X-spell=0, X=1, XX=2)
# 4       generic mana
# 5       hybrid mana
# 6 to 10 devotion to W-U-B-R-G
# 11      legendary flag
# 12      articact flag
# 13      enchantment flag
inputVecs = [[]] * len(data)

inputWords = [] #list of lists of words
ptDict = {"*": "0", "1+*": "1"} #converts */* creatures and Goyf

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
    inputWords.append(orTxt.split(" ")) #split into word tokens

    #parse numeric data
    types = card["type_line"].split(" ") #get card types
    mana = card["mana_cost"]
    genNums = re.findall("[0-9]", mana) #get generic component of mana cost (None if no generic component)
    inputVec = [int(ptDict.get(card["power"], card["power"])),
                int(ptDict.get(card["toughness"], card["toughness"])),
                int(card["cmc"]),
                sum([int(i) for i in genNums]), #parse generic mana cost
                mana.count("X"), #parse mana stats
                mana.count("/"),
                mana.count("W"),
                mana.count("U"),
                mana.count("B"),
                mana.count("R"),
                mana.count("G"),
                1 if "Legendary" in types else 0, #parse type flags
                1 if "Artifact" in types else 0,
                1 if "Enchantment" in types else 0]
    inputVecs.append(inputVec)
    print(card["name"] + ": " + str(inputVec))
