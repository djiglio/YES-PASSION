import cloudscraper
import re
import json

def test_tm_history(player_url):
    scraper = cloudscraper.create_scraper()
    scraper.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    })
    
    # transform profile URL to marktwertverlauf
    # e.g., /cristiano-ronaldo/profil/spieler/8198 -> /cristiano-ronaldo/marktwertverlauf/spieler/8198
    history_url = f"https://www.transfermarkt.it{player_url.replace('/profil/', '/marktwertverlauf/')}"
    print(f"Fetching history {history_url} ...")
    
    response = scraper.get(history_url)
    if response.status_code == 200:
        print("Success! Parsing chart data...")
        # The data is inside a script tag like: 'data': [{'y': 100000000, 'datum_mw': 'May 28, 2018' ...}]
        # We can look for "series" in the highcharts definition
        match = re.search(r"'series':\s*\[\{.*?\'data\':\s*(\[.*?\])\}\]", response.text, re.DOTALL)
        if match:
            # We need to be careful with eval, but let's try a regex approach or json.loads by cleaning it up
            # Actually, the format is standard JSON but with single quotes or unquoted keys sometimes.
            # Let's just regex find all 'y': (\d+),.*?datum_mw': '(.*?)'
            points = re.findall(r"'y':(\d+),.*?'datum_mw':'(.*?)'", response.text.replace(' ', ''))
            print("Found points:")
            for p in points:
                print(f"Value: {p[0]}, Date: {p[1]}")
        else:
            print("Could not find Highcharts data in the page source.")
    else:
        print("Failed to fetch history.")

if __name__ == "__main__":
    test_tm_history("/cristiano-ronaldo/profil/spieler/8198")
