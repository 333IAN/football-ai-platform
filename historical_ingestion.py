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
    team = session.query(Team).filter_by(team_id=team_id).first()
    if not team:
        team = Team(team_id=team_id, name=team_name)
        session.add(team)
        session.commit()
    return team

def fetch_recent_finished_tournaments():
    # Using the IDs for recently finished tournaments!
    tournaments = [
        {"name": "Euro 2024", "stage_id": "EcpQtcVi"},
        {"name": "Copa America 2024", "stage_id": "zDzsPsN5"}
    ]
    
    total_added = 0
    
    for t in tournaments:
        print(f"Fetching historical results for {t['name']}...")
        url = "https://flashlive-sports.p.rapidapi.com/v1/tournaments/results" 
        querystring = {"locale": "en_INT", "tournament_stage_id": t['stage_id'], "page": "1"}
        
        response = requests.get(url, headers=headers, params=querystring)
        
        if response.status_code != 200:
            print(f"Error fetching {t['name']}:", response.text)
            continue

        data = response.json()
        
        # Safely extract the events array
        data_block = data.get('DATA', [])
        if not data_block:
            print(f"No data returned for {t['name']}")
            continue
            
        events = data_block[0].get('EVENTS', [])
        
        match_count = 0
        for event in events:
            # We ONLY want matches that have actually finished
            if event.get('STAGE_TYPE') != 'FINISHED':
                continue

            match_id = event['EVENT_ID']
            match_date = datetime.fromtimestamp(event['START_TIME'])
            
            home_id = event['HOME_PARTICIPANT_IDS'][0]
            home_name = event['HOME_NAME']
            home_score = int(event.get('HOME_SCORE_CURRENT', 0)) 
            
            away_id = event['AWAY_PARTICIPANT_IDS'][0]
            away_name = event['AWAY_NAME']
            away_score = int(event.get('AWAY_SCORE_CURRENT', 0))

            get_or_create_team(home_id, home_name)
            get_or_create_team(away_id, away_name)

            existing_match = session.query(Match).filter_by(match_id=match_id).first()
            if not existing_match:
                new_match = Match(
                    match_id=match_id,
                    home_team_id=home_id,
                    away_team_id=away_id,
                    match_date=match_date,
                    competition_name=t['name'],
                    home_score=home_score,
                    away_score=away_score,
                    status="FINISHED"
                )
                session.add(new_match)
                match_count += 1
                total_added += 1
                print(f"  [+] Result Added: {home_name} {home_score} - {away_score} {away_name}")
        
        try:
            session.commit()
            print(f"-> Saved {match_count} matches for {t['name']}\n")
        except Exception as e:
            session.rollback()
            print(f"Database error saving {t['name']}: {e}")

    print(f"Success! A total of {total_added} historical matches are now in the database.")

if __name__ == "__main__":
    fetch_recent_finished_tournaments()