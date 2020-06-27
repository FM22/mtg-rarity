import json
import re
import unidecode
import numpy as np
from gensim.models import Word2Vec
import tensorflow as tf
from tensorflow.keras.layers.experimental.preprocessing import Normalization
from tensorflow.keras import layers
from tensorflow import keras

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
# 6 to 10 devotion to W-U-B-R-G
# 11      legendary flag
# 12      articact flag
# 13      enchantment flag
inputVecs = []

inputWords = [] #list of lists of words
corRars = [] #list of correct rarities
ptDict = {"*": "0", "1+*": "1"} #converts */* creatures and Goyf
rarDict = {"common": 0, "uncommon": 1, "rare": 2, "mythic": 3} #converts rarity to target output index
invRarDict = {v: k for k, v in rarDict.items()} #inversion (for output)

#extract data
for card in data:
    #parse oracle text
    orTxt = card["oracle_text"]
    orTxt = unidecode.unidecode(orTxt) #fix utf-8 (mostly en-dashes)
    orTxt = re.sub(card["name"], "CARDNAME", orTxt) #replace instances of self reference
    shortName = re.search("^.*\,", card["name"]) #name of legends before first comma e.g. *Garza Zol*, Plague Queen
    if not shortName == None: orTxt = re.sub(shortName.group()[:-1], "CARDNAME", orTxt) #replace self reference by short name
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
    corRars.append(rarDict[card["rarity"]])
print("Parsed data")

#vectorise words
w2vModel = Word2Vec(inputWords, min_count = 1) #train word2vec model
print("Vectorised oracle text")

#split data into training and test datasets
testNames = [data[i]["name"] for i in range(len(data)) if data[i]["set"] == "m20"]
trainVecs = [inputVecs[i] for i in range(len(inputVecs)) if not data[i]["set"] == "m20"]
testVecs = [inputVecs[i] for i in range(len(inputVecs)) if data[i]["set"] == "m20"]
trainWords = [inputWords[i] for i in range(len(inputWords)) if not data[i]["set"] == "m20"]
testWords = [inputWords[i] for i in range(len(inputWords)) if data[i]["set"] == "m20"]
trainCorRars = [corRars[i] for i in range(len(corRars)) if not data[i]["set"] == "m20"]
testCorRars = [corRars[i] for i in range(len(corRars)) if data[i]["set"] == "m20"]

#put words through word2vec model
trainWords = [[w2vModel[w] for w in t] for t in trainWords]
testWords = [[w2vModel[w] for w in t] for t in testWords]

#normalise intput vectors
trainVecs = np.array(trainVecs).astype("float32") #convert to numpy format
normalizer = Normalization()
normalizer.adapt(trainVecs)
trainVecs = normalizer(trainVecs)
testVecs = normalizer(testVecs)
print("Normalised numerical data")

#build keras model
wordIn = layers.Input(shape = (None, 100)) #input layer for var-length word vec data
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
print(pred)
pred = [np.where(a == np.amax(a))[0][0] for a in pred] #get most likely outcome (idk why I need [0][0])
for i in range(len(pred)): #display visual version of above test
    print(testNames[i] + ": guess - " + invRarDict[pred[i]] + ", actual - " + invRarDict[testCorRars[i]] + "; " + ("correct" if pred[i] == testCorRars[i] else "wrong"))