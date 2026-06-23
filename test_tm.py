import cloudscraper
from bs4 import BeautifulSoup
import json

def test_tm_search(query):
    scraper = cloudscraper.create_scraper()
    # Transfermarkt requires a realistic User-Agent
    scraper.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    })
    
    url = f"https://www.transfermarkt.it/schnellsuche/ergebnis/schnellsuche?query={query}"
    print(f"Fetching {url} ...")
    response = scraper.get(url)
    
    if response.status_code == 200:
        print("Success! Parsing HTML...")
        soup = BeautifulSoup(response.text, 'lxml')
        # Find first search result
        table = soup.find('table', {'class': 'items'})
        if table:
            first_row = table.find('tbody').find('tr')
            tds = first_row.find_all('td')
            # Typically td with class 'hauptlink' has the player link
            hauptlink = first_row.find('td', {'class': 'hauptlink'})
            if hauptlink:
                a = hauptlink.find('a')
                if a:
                    print(f"Found player: {a.text} -> {a['href']}")
                    return
        print("Table or link not found.")
    else:
        print(f"Failed with status code: {response.status_code}")

if __name__ == "__main__":
    test_tm_search("Cristiano Ronaldo")
