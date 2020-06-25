import urllib.request
import urllib.parse
import sys
import json

cardList = []
nextPg = True

with open("query.txt", "r") as f:
	query = f.read()
print("Query is " + query)

nxtUrl = "https://api.scryfall.com/cards/search?q=" + urllib.parse.quote(query)
print("Reading from " + nxtUrl)

i = 1
while nextPg == True:
	data = json.load(urllib.request.urlopen(nxtUrl))
	if "next_page" in data:
		nxtUrl = data["next_page"]
	else: nextPg = False
	print("Read page " + str(i))
	i += 1
	cardList.extend(data["data"])

with open("data.json", "w+", encoding = "utf8") as f:
	json.dump(cardList, f, ensure_ascii = False)
print("Written data to data.json")