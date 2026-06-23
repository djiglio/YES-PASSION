import os
import json
import urllib.request
import urllib.parse
import random
import time
import concurrent.futures

data_dir = os.path.join(os.path.dirname(__file__), 'data', 'seasons')

# Shared cache for birth years
birth_years = {}

def fetch_birth_year(name):
    if name in birth_years: return name, birth_years[name]
    
    try:
        # Step 1: Search Wikipedia for the player
        q = urllib.parse.quote(f"{name} footballer")
        url = f'https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={q}&utf8=&format=json'
        req = urllib.request.Request(url, headers={'User-Agent': 'YesPassionApp/1.0 (Contact: me@example.com)'})
        r = urllib.request.urlopen(req, timeout=5)
        data = json.loads(r.read())
        
        if not data['query']['search']:
            return name, None
            
        title = data['query']['search'][0]['title']
        
        # Step 2: Get Wikidata item for this Wikipedia page
        title_q = urllib.parse.quote(title)
        url_wd = f"https://en.wikipedia.org/w/api.php?action=query&prop=pageprops&titles={title_q}&format=json"
        req_wd = urllib.request.Request(url_wd, headers={'User-Agent': 'YesPassionApp/1.0'})
        r_wd = urllib.request.urlopen(req_wd, timeout=5)
        data_wd = json.loads(r_wd.read())
        
        pages = data_wd['query']['pages']
        page = list(pages.values())[0]
        if 'pageprops' not in page or 'wikibase_item' not in page['pageprops']:
            return name, None
            
        wb_id = page['pageprops']['wikibase_item']
        
        # Step 3: Get birth date from Wikidata
        url_claim = f"https://www.wikidata.org/w/api.php?action=wbgetclaims&entity={wb_id}&property=P569&format=json"
        req_claim = urllib.request.Request(url_claim, headers={'User-Agent': 'YesPassionApp/1.0'})
        r_claim = urllib.request.urlopen(req_claim, timeout=5)
        data_claim = json.loads(r_claim.read())
        
        if 'claims' in data_claim and 'P569' in data_claim['claims']:
            time_str = data_claim['claims']['P569'][0]['mainsnak']['datavalue']['value']['time']
            year = int(time_str[1:5])
            return name, year
            
        return name, None
    except Exception as e:
        return name, None

def calculate_value_and_age(name, ovr, season_year):
    try:
        ovr = int(ovr)
    except:
        return "€0", 0, 25
        
    b_year = birth_years.get(name)
    if not b_year:
        # Fallback se la ricerca fallisce
        b_year = season_year - 25
        
    age = season_year - b_year
    
    if age < 15: age = 15
    if age > 45: age = 45
        
    val = 0
    if ovr >= 90:
        val = 60 + (ovr - 90) * 15
    elif ovr >= 85:
        val = 25 + (ovr - 85) * 7
    elif ovr >= 80:
        val = 12 + (ovr - 80) * 2.5
    elif ovr >= 75:
        val = 4 + (ovr - 75) * 1.5
    elif ovr >= 70:
        val = 1.5 + (ovr - 70) * 0.5
    elif ovr >= 65:
        val = 0.5 + (ovr - 65) * 0.2
    else:
        val = 0.2
        
    # Age multiplier
    if age <= 21:
        val *= 1.6
    elif age <= 24:
        val *= 1.2
    elif age <= 28:
        val *= 1.0
    elif age <= 31:
        val *= 0.7
    else:
        val *= 0.4
        
    # Deterministic variance based on name length so it doesn't fluctuate randomly every time
    variance = ((len(name) % 10) / 100.0) - 0.05
    val = val * (1 + variance)
    
    numeric_val = val * 1000000
    
    if val >= 1:
        formatted = f"€{round(val, 1)}M"
    else:
        formatted = f"€{int(round(val * 1000))}K"
        
    return formatted, numeric_val, age

def main():
    print("Reading all names...")
    names_to_fetch = set()
    files = sorted([f for f in os.listdir(data_dir) if f.endswith('.json')])
    for filename in files:
        with open(os.path.join(data_dir, filename), 'r', encoding='utf-8') as f:
            data = json.load(f)
            for team in data.get('teams', []):
                for player in team.get('players', []):
                    names_to_fetch.add(player['Nome'])
                    
    names_list = list(names_to_fetch)
    print(f"Found {len(names_list)} unique players. Fetching real birth years from Wikipedia/Wikidata...")
    
    # Use ThreadPool to speed up
    fetched_count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(fetch_birth_year, name): name for name in names_list}
        for future in concurrent.futures.as_completed(futures):
            name, year = future.result()
            fetched_count += 1
            if year:
                birth_years[name] = year
            if fetched_count % 100 == 0:
                print(f"Progress: {fetched_count}/{len(names_list)}...")

    print("Updating datasets with real ages...")
    all_players = []
    
    for filename in files:
        season_id = filename.split('_')[1].split('.')[0]
        filepath = os.path.join(data_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        season_name = data.get('season_name', f"20{season_id}")
        season_year = int("20" + season_id)
            
        for team in data.get('teams', []):
            for player in team.get('players', []):
                ovr = player.get('Overall', 0)
                formatted_val, num_val, age = calculate_value_and_age(player['Nome'], ovr, season_year)
                player['Value'] = formatted_val
                player['ValueNum'] = num_val
                player['Age'] = age
                
                all_players.append({
                    'name': player['Nome'],
                    'club': team['name'],
                    'season': season_name,
                    'ovr': ovr,
                    'age': age,
                    'val_num': num_val,
                    'val_str': formatted_val
                })
                        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    all_players.sort(key=lambda x: x['val_num'], reverse=True)
    print("\n--- TOP 5 MOST EXPENSIVE PLAYERS (REAL AGES) ---")
    for i in range(5):
        p = all_players[i]
        print(f"{i+1}. {p['name']} ({p['club']}) - Season: {p['season']} | OVR: {p['ovr']} | Real Age: {p['age']} | Value: {p['val_str']}")

if __name__ == "__main__":
    main()
