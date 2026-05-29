import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_FOOTBALL_KEY") 


url = "https://free-api-live-football-data.p.rapidapi.com/football-all-search?search=world%20cup" 

headers = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "free-api-live-football-data.p.rapidapi.com"
}

# Some APIs require a query parameter to search
querystring = {"name": "World Cup"} 

print("Pinging SportAPI7...")
response = requests.get(url, headers=headers, params=querystring)

if response.status_code == 200:
    data = response.json()
    
    print(json.dumps(data, indent=4))
else:
    print(f"Failed with status code: {response.status_code}")
    print(response.text)