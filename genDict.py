import json
import unidecode
import re

#read and parse the datafile
with open("data.json", encoding = "utf8") as f:
    data = json.load(f)
print("Read data.json")

#words generated during text cleanup in run.py
words = {"plus", "minus", "blue", "black", "red", "green", "or", "tap", "colorless", "energy", "snow", "untap", "two", "life"}

for card in data:
    #get relevant word tokens
    orTxt = card["oracle_text"]
    orTxt = unidecode.unidecode(orTxt) #fix utf-8 (mostly en-dashes)
    orTxt = re.sub(card["name"], "this permanent", orTxt) #replace instances of self reference
    shortName = re.search("^.*?\,", card["name"]) #name of legends before first comma e.g. *Garza Zol*, Plague Queen
    if not shortName == None: orTxt = re.sub(shortName.group()[:-1], "this permanent", orTxt) #replace shortened self reference
    orTxt = re.sub("\(.*?\)", "", orTxt) #strip out reminder text (text in brackets)
    orTxt = re.sub("\,|\.|--|;|:|\"|\*|\/", " ", orTxt) #remove all punctuation
    orTxt = re.sub("'", "", orTxt)  #remove apostrophes
    words.update(w for w in orTxt.lower().split(" ") if w.isalnum()) #grab all alphanumeric tokens
print("Found all tokens")
print(words)
#write over the relevant section of dictionary from the GloVe file
gloveDict = {}
with open("glove.txt", encoding = "utf-8") as glove:
    with open("dict.txt", "w", encoding = "utf-8") as out:
        for line in glove:
            if(line.split(" ")[0] in words): #only save words we will actually look up for memory reasons
                print(line.split(" ")[0])
                out.write(line)