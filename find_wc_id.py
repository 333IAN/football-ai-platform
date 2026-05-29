import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_FOOTBALL_KEY")

headers = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "flashlive-sports.p.rapidapi.com"
}

def search_for_tournament(search_term):
    print(f"Searching for tournament: '{search_term}'...")
    
    url = "https://flashlive-sports.p.rapidapi.com/v1/tournaments/list?locale=en_INT"
    querystring = {"locale": "en_INT", "query": search_term}
    
    response = requests.get(url, headers=headers, params=querystring)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return

    data = response.json()
    
    # The 'DATA' array usually contains different categories. We want the one for Tournaments.
    results = data.get('DATA', [])
    
    found = False
    for category in results:
        if category.get('NAME') == 'TOURNAMENTS':
            tournaments = category.get('ITEMS', [])
            print(f"\n--- Found {len(tournaments)} Tournaments matching '{search_term}' ---")
            
            for t in tournaments:
                print(f"Name: {t.get('NAME')}")
                print(f"Country: {t.get('COUNTRY_NAME')}")
                print(f"Tournament ID: {t.get('TOURNAMENT_ID')}")
                print(f"Stage ID: {t.get('TOURNAMENT_STAGE_ID')}")
                print(f"Template ID: {t.get('TOURNAMENT_TEMPLATE_ID')}")
                print("-" * 30)
            found = True
            break
            
    if not found:
        print("\nCould not find a TOURNAMENTS section in the search results.")
        # Print the raw data so we can inspect what the API actually returned
        print(json.dumps(data, indent=2)[:1000] + "...\n(Truncated)")

if __name__ == "__main__":
    search_for_tournament("World Cup")