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
	raw = urllib.request.urlopen(nxtUrl).read()
	data = json.loads(raw)
	if "next_page" in data:
		nxtUrl = data["next_page"]
	else: nextPg = False
	print("Read page " + str(i))
	i += 1
	cardList.extend(data["data"])

txt = json.dumps(cardList)
with open("data.json", "w+") as f:
	f.write(txt)
print("Written data to data.json")