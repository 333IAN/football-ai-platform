import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
# Assuming you replaced the API key in your .env with your new RapidAPI key
API_KEY = os.getenv("API_FOOTBALL_KEY") 

# IMPORTANT: You must replace this URL with the exact Tournaments/Search 
# endpoint provided in the SportAPI7 RapidAPI documentation.
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
    # This will print the raw JSON to your terminal beautifully formatted
    # so you can manually hunt for the World Cup ID and see the dictionary keys.
    print(json.dumps(data, indent=4))
else:
    print(f"Failed with status code: {response.status_code}")
    print(response.text)