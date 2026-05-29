import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from database_setup import engine, Team, Match

load_dotenv()
API_KEY = os.getenv("API_FOOTBALL_KEY")

Session = sessionmaker(bind=engine)
session = Session()

headers = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "flashlive-sports.p.rapidapi.com"
}

def get_or_create_team(team_id, team_name):
    """Checks if a team exists. If not, adds it to the database."""
    team = session.query(Team).filter_by(team_id=team_id).first()
    if not team:
        team = Team(team_id=team_id, name=team_name)
        session.add(team)
        session.commit()
        print(f"  [+] New Team Added: {team_name}")
    return team

def fetch_world_cup_matches():
    print("Fetching World Cup 2026 Fixtures...")
    
    # Replace with the exact URL you used to get the fixtures
    url = "https://flashlive-sports.p.rapidapi.com/v1/tournaments/fixtures?locale=en_INT&tournament_stage_id=SbLsX4y7&page=1" 
    querystring = {"locale": "en_INT", "tournament_stage_id": "SbLsX4y7", "page": "1"}
    
    response = requests.get(url, headers=headers, params=querystring)
    
    if response.status_code != 200:
        print("Error fetching data:", response.text)
        return

    data = response.json()
    events = data.get('DATA', [])[0].get('EVENTS', [])
    
    match_count = 0

    for event in events:
        match_id = event['EVENT_ID']
        
        # Convert Unix timestamp to Python DateTime
        match_date = datetime.fromtimestamp(event['START_TIME'])
        
        home_id = event['HOME_PARTICIPANT_IDS'][0]
        home_name = event['HOME_NAME']
        
        away_id = event['AWAY_PARTICIPANT_IDS'][0]
        away_name = event['AWAY_NAME']
        
        status = event['STAGE_TYPE']

        # 1. Ensure both teams exist in our database
        get_or_create_team(home_id, home_name)
        get_or_create_team(away_id, away_name)

        # 2. Add the match
        existing_match = session.query(Match).filter_by(match_id=match_id).first()
        if not existing_match:
            new_match = Match(
                match_id=match_id,
                home_team_id=home_id,
                away_team_id=away_id,
                match_date=match_date,
                competition_name="FIFA World Cup 2026",
                status=status
            )
            session.add(new_match)
            match_count += 1
            print(f"  [+] Match Added: {home_name} vs {away_name} on {match_date}")

    try:
        session.commit()
        print(f"\nSuccess! Added {match_count} World Cup matches to the database.")
    except Exception as e:
        session.rollback()
        print(f"Database error: {e}")

if __name__ == "__main__":
    fetch_world_cup_matches()