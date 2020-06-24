import urllib.request
import sys
import json

i=0
cardList = []
nextPg = True

if len(sys.argv) < 0:
  print("Specify a query to get")
else:
  nxtUrl = "https://api.scryfall.com/cards/search?q=" + sys.argv[1]
  
  while nextPg == True:
    raw = urllib.request.urlopen(nxtUrl).read()
    data = json.loads(raw)
    if "next_page" in data:
      nxtUrl = data["next_page"]
    else: nextPg = False
    cardList.extend (data["data"])
    print("Page "+str(i)+" read")
    i += 1

  txt = json.dumps(cardList)

  with open("data.json", "w+") as f:
    f.write(txt)
