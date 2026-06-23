import requests
import json

url = 'https://query.wikidata.org/sparql'
query = """
SELECT ?itemLabel ?dob WHERE {
  ?item wdt:P31 wd:Q5;          # instance of human
        wdt:P106 wd:Q937857;     # occupation: association football player
        wdt:P569 ?dob.           # date of birth
  SERVICE wikibase:label { bd:serviceParam wikibase:language "it,en". }
}
LIMIT 10
"""

r = requests.get(url, params={'format': 'json', 'query': query}, headers={'User-Agent': 'YesPassionApp/1.0 (test)'})
print(r.status_code)
if r.status_code == 200:
    data = r.json()
    for item in data['results']['bindings']:
        print(item['itemLabel']['value'], item['dob']['value'])
