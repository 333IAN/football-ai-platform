import os
import requests
from dotenv import load_dotenv

# 1. Initialize environment and headers
load_dotenv()
API_KEY = os.getenv("API_FOOTBALL_KEY")

headers = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "flashlive-sports.p.rapidapi.com"
}

def find_tournament_metadata(search_keyword):
    """
    Downloads the entire soccer tournament directory and filters 
    for leagues or cups matching the search keyword.
    """
    print(f"Pinging FlashLive directory for keyword: '{search_keyword}'...\n")
    
    url = "https://flashlive-sports.p.rapidapi.com/v1/tournaments/list"
    querystring = {"locale": "en_INT", "sport_id": "1"} # 1 = Soccer
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
    except Exception as e:
        print(f"[!] Network error: {e}")
        return

    if response.status_code != 200:
        print(f"[!] API Error {response.status_code}: {response.text}")
        return

    payload = response.json()
    tournaments_list = payload.get("DATA", [])
    
    match_count = 0
    print(f"==================================================")
    print(f" MATCHING TOURNAMENT TEMPLATES FOUND")
    print(f"==================================================")

    for item in tournaments_list:
        league_name = item.get("LEAGUE_NAME", "")
        country_name = item.get("COUNTRY_NAME", "")
        
        # Perform a case-insensitive search check
        if search_keyword.lower() in league_name.lower():
            match_count += 1
            print(f"Competition: {country_name}: {league_name}")
            print(f"  -> Tournament Season ID : {item.get('ACTUAL_TOURNAMENT_SEASON_ID')}")
            print(f"  -> Template ID         : {item.get('TOURNAMENT_TEMPLATE_ID')}")
            
            # Print out any active sub-stages attached to this block
            stages = item.get("STAGES", [])
            if stages:
                print("  -> Inner Stage IDs:")
                for stage in stages:
                    print(f"     * [{stage.get('STAGE_NAME')}] -> ID: {stage.get('STAGE_ID')}")
            print("-" * 50)

    if match_count == 0:
        print(f"No tournaments found matching '{search_keyword}'.")
        print("Try keywords like 'Cup', 'Euro', 'Copa', or specific country names.")
    else:
        print(f"Found {match_count} records. Use the Stage IDs above for your pipeline.")

if __name__ == "__main__":
    # Change this string to search for different competitions (e.g., "Euro", "Copa America")
    TARGET_SEARCH = "Copa America"
    find_tournament_metadata(TARGET_SEARCH)