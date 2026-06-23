import urllib.request
import json
import urllib.parse
import time

def get_birth_year(name):
    try:
        # Step 1: Search Wikipedia for the player
        q = urllib.parse.quote(f"{name} footballer")
        url = f'https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={q}&utf8=&format=json'
        req = urllib.request.Request(url, headers={'User-Agent': 'YesPassionApp/1.0'})
        r = urllib.request.urlopen(req)
        data = json.loads(r.read())
        
        if not data['query']['search']:
            return None
            
        title = data['query']['search'][0]['title']
        
        # Step 2: Get Wikidata item for this Wikipedia page
        title_q = urllib.parse.quote(title)
        url_wd = f"https://en.wikipedia.org/w/api.php?action=query&prop=pageprops&titles={title_q}&format=json"
        req_wd = urllib.request.Request(url_wd, headers={'User-Agent': 'YesPassionApp/1.0'})
        r_wd = urllib.request.urlopen(req_wd)
        data_wd = json.loads(r_wd.read())
        
        pages = data_wd['query']['pages']
        page = list(pages.values())[0]
        if 'pageprops' not in page or 'wikibase_item' not in page['pageprops']:
            return None
            
        wb_id = page['pageprops']['wikibase_item']
        
        # Step 3: Get birth date from Wikidata
        url_claim = f"https://www.wikidata.org/w/api.php?action=wbgetclaims&entity={wb_id}&property=P569&format=json"
        req_claim = urllib.request.Request(url_claim, headers={'User-Agent': 'YesPassionApp/1.0'})
        r_claim = urllib.request.urlopen(req_claim)
        data_claim = json.loads(r_claim.read())
        
        if 'claims' in data_claim and 'P569' in data_claim['claims']:
            time_str = data_claim['claims']['P569'][0]['mainsnak']['datavalue']['value']['time']
            # Format: +1993-11-15T00:00:00Z
            year = int(time_str[1:5])
            return year
            
        return None
    except Exception as e:
        print(f"Error for {name}: {e}")
        return None

print("C. Ronaldo ->", get_birth_year("C. Ronaldo"))
print("P. Dybala ->", get_birth_year("P. Dybala"))
print("M. Benatia ->", get_birth_year("M. Benatia"))
