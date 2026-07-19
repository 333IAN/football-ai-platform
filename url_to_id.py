import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_FOOTBALL_KEY")


MATCH_ID = "rBfk6fO7"

response = requests.get(
    "https://flashlive-sports.p.rapidapi.com/v1/events/data",
    headers={
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "flashlive-sports.p.rapidapi.com"
    },
    params={"locale": "en_INT", "event_id": MATCH_ID}
)

data = response.json()
print(json.dumps(data, indent=2))