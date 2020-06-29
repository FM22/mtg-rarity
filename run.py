import json
import re
import unidecode
import numpy as np
from gensim.models import Word2Vec
import tensorflow as tf
from tensorflow.keras.layers.experimental.preprocessing import Normalization
from tensorflow.keras import layers
from tensorflow import keras
from num2words import num2words

#read and parse the datafile
with open("data.json", encoding = "utf8") as f:
    data = json.load(f)
print("Read data.json")

# list of input vectors
# index   value
# 0       power
# 1       toughness
# 2       cmc
# 3       X spell counter (non-X-spell=0, X=1, XX=2)
# 4       generic mana
# 5       hybrid mana
# 6 to 11 devotion to W-U-B-R-G
# 12      legendary flag
# 13      articact flag
# 14      enchantment flag
inputVecs = []

inputWords = [] #list of lists of words
corRars = [] #list of correct rarities
ptDict = {"*": "0", "1+*": "1"} #converts */* creatures and Goyf
rarDict = {"common": 0, "uncommon": 1, "rare": 2, "mythic": 3} #converts rarity to target output index
invRarDict = {v: k for k, v in rarDict.items()} #inversion (for output)
symbDict = {"W": " white ", #symbol parser for within {} - X,Y and numbers kept as is
            "U": " blue ",
            "B": " black ",
            "R": " red ",
            "G": " green ",
            "/": " or ",
            "T": " tap ",
            "C": " colorless ",
            "E": " energy ",
            "S": " snow ",
            "Q": " untap ",
            "P": " two life ",
            "{": " ", "}": " "} #delete the brackets
commonApos = {"don't", "can't", "wasn't", "didn't", "it's", "you're", "they're", "he's", "she's"} #ad hoc - trying to optimise the vectors

#extract data
for card in data:
    #parse oracle text
    orTxt = card["oracle_text"]
    orTxt = unidecode.unidecode(orTxt) #fix utf-8 (mostly en-dashes)
    orTxt = re.sub(card["name"], "this permanent", orTxt) #replace instances of self reference
    shortName = re.search("^.*?\,", card["name"]) #name of legends before first comma e.g. *Garza Zol*, Plague Queen
    if not shortName == None: orTxt = re.sub(shortName.group()[:-1], "this permanent", orTxt) #replace shrtened self reference
    orTxt = re.sub("\(.*?\)", "", orTxt) #strip out reminder text (text in brackets)
    orTxt = re.sub("\n", " . ", orTxt) #replace newlines with full stops
    orTxt = re.sub("$", " .", orTxt) #replace eol with full stops
    orTxt = re.sub("\+", " plus ", orTxt) #write out '+'
    orTxt = re.sub("\-", " minus ", orTxt) #write out '-'
    orTxt = re.sub("\,|\.|--|;|:|\"", " \g<0> ", orTxt) #add spacing around standard punctuation
    orTxt = re.sub("\*|\/|'", " ", orTxt) #remove non-stadard punctuation and apostrophes
    indices = [i for m in re.finditer("\{.*?\}", orTxt) for i in range(m.start(), m.end())] #find all indices within curly brakets
    orTxt = "".join([(symbDict.get(orTxt[i], orTxt[i])) if i in indices else orTxt[i] for i in range(len(orTxt))]) #interpret naturally symbols in curly brackets
    orTxt = re.sub("[ ]+", " ", orTxt) #remove any generated multiple spaces
    orTxt = re.sub("\. \.", ".", orTxt) #remove any generated multiple full stops
    orTxt = re.sub("^\.", "", orTxt) #remove leading full stops (due to newlines/eol)
    orTxt = re.sub("( $|^ )", "", orTxt) #remove leading and trailing spaces
    orTxt = orTxt.lower().split(" ") #split up text into word tokens and remove capital letters
    inputWords.append(orTxt)

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
                mana.count("C"),
                1 if "Legendary" in types else 0, #parse type flags
                1 if "Artifact" in types else 0,
                1 if "Enchantment" in types else 0]
    inputVecs.append(inputVec)
    corRars.append(rarDict[card["rarity"]])
print("Parsed data")

allWords = set([w for t in inputWords for w in t]) #list all word tokens
#generate the relevant section of dictionary from the GloVe file
gloveDict = {}
with open("glove.txt", encoding="utf-8") as glove:
    for line in glove:
        parts = line.split(" ")
        if(parts[0] in allWords): #only save words we will actually look up for memory reasons
            gloveDict[parts[0]] = [float(i) for i in parts[1:]]
inputWords = [[gloveDict.get(w, [0] * 100) for w in t] for t in inputWords] #vectorise words: if the word is unique to MTG it just gets set to 0
print(allWords - set(gloveDict.keys()))
print("Vectorised oracle text")

#split data into training and test datasets
testNames = [data[i]["name"] for i in range(len(data)) if data[i]["set"] == "m20"]
trainVecs = [inputVecs[i] for i in range(len(inputVecs)) if not data[i]["set"] == "m20"]
testVecs = [inputVecs[i] for i in range(len(inputVecs)) if data[i]["set"] == "m20"]
trainWords = [inputWords[i] for i in range(len(inputWords)) if not data[i]["set"] == "m20"]
testWords = [inputWords[i] for i in range(len(inputWords)) if data[i]["set"] == "m20"]
trainCorRars = [corRars[i] for i in range(len(corRars)) if not data[i]["set"] == "m20"]
testCorRars = [corRars[i] for i in range(len(corRars)) if data[i]["set"] == "m20"]

#normalise input vectors
trainVecs = np.array(trainVecs).astype("float32") #convert to numpy format
normalizer = Normalization()
normalizer.adapt(trainVecs)
trainVecs = normalizer(trainVecs)
testVecs = normalizer(testVecs)
print("Normalised numerical data")

#build keras model
wordIn = layers.Input(shape = (None, 300)) #input layer for var-length word vec data
numIn = layers.Input(shape = (len(inputVecs[0]), )) #input layer for fixed-length numerical data
rnn = layers.LSTM(32)(wordIn) #RNN layer for word vec data
numLayer = layers.Dense(16, activation = "relu")(numIn) #layer for numerical data
merge = layers.concatenate([rnn, numLayer]) #combine the two vectors
combLayer = layers.Dense(64, activation = "relu")(merge) #hidden intermediate layer for combined data
out = layers.Dense(4, activation = "softmax")(combLayer) #final layer: softmax ensures output is a set of probabilities
model = keras.models.Model(inputs = [wordIn, numIn], outputs = [out])
model.compile(loss = "sparse_categorical_crossentropy", metrics = "sparse_categorical_accuracy") #I have no idea whether these ones are the best ones to use
print("Built model")

#train the model
model.fit([tf.ragged.constant(trainWords), trainVecs], np.array(trainCorRars), epochs = 10)
print("Trained model")

#test the model
model.evaluate([tf.ragged.constant(testWords), testVecs], np.array(testCorRars))
pred = model.predict([tf.ragged.constant(testWords), testVecs])
pred = [np.where(a == np.amax(a))[0][0] for a in pred] #get most likely outcome (idk why I need [0][0])
for i in range(len(pred)): #display visual version of above test
    if not pred[i] == testCorRars[i]: print(testNames[i] + ": guess - " + invRarDict[pred[i]] + ", actual - " + invRarDict[testCorRars[i]] + "; " + ("correct" if pred[i] == testCorRars[i] else "wrong"))