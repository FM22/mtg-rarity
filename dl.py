import urllib.request
import sys
import json

i=0
cardList = []
nextPg = True
nxtUrl = "https://api.scryfall.com/cards/search?q=layout%3Anormal+t%3Acreature+(set%3A10E+or+set%3AM10+or+set%3AM11+or+set%3AM12+or+set%3AM13+or+set%3AM14+or+set%3AM15+or+set%3AORI+or+set%3AM19+or+set%3AM20+or+set%3AM21+or+set%3AMRD+or+set%3ADST+or+set%3A5DN+or+set%3ACHK+or+set%3ABOK+or+set%3ASOK+or+set%3ARAV+or+set%3AGPT+or+set%3ADIS+or+set%3ACSP+or+set%3ATSP+or+set%3ATSB+or+set%3APLC+or+set%3AFUT+or+set%3ALRW+or+set%3AMOR+or+set%3ASHM+or+set%3AEVE+or+set%3AALA+or+set%3ACON+or+set%3AARB+or+set%3AZEN+or+set%3AWWK+or+set%3AROE+or+set%3ASOM+or+set%3AMBS+or+set%3ANPH+or+set%3AISD+or+set%3ADKA+or+set%3AAVR+or+set%3ARTR+or+set%3AGTC+or+set%3ADGM+or+set%3ATHS+or+set%3ABNG+or+set%3AJOU+or+set%3AKTK+or+set%3AFRF+or+set%3ADTK+or+set%3ABFZ+or+set%3AOGW+or+set%3ASOI+or+set%3AEMN+or+set%3AKLD+or+set%3AAER+or+set%3AAKH+or+set%3AHOU+or+set%3AXLN+or+set%3ARIX+or+set%3ADOM+or+set%3AGRN+or+set%3ARNA+or+set%3AWAR+or+set%3AELD+or+set%3ATHB+or+set%3AIKO)"

if len(sys.argv) < 0:
  print("Specify a query to get")
else:
  nxtUrl = sys.argv[1]
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
