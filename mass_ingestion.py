import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from database_setup import engine, Team, Match

# 1. Environment variables and database session
load_dotenv()
API_KEY = os.getenv("API_FOOTBALL_KEY")

Session = sessionmaker(bind=engine)
session = Session()

# 2. Authentication headers
headers = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "flashlive-sports.p.rapidapi.com"
}

# 3. Master Task Registry
# This handles different endpoints, stages, and match statuses seamlessly.
SCRAPING_TASKS = [
    {
        "name": "Euro 2024",
        "url": "https://flashlive-sports.p.rapidapi.com/v1/tournaments/results",
        "stage_id": "EcpQtcVi",
        "target_status": "FINISHED"
    },
    {
        "name": "FIFA Club World Cup (Main)",
        "url": "https://flashlive-sports.p.rapidapi.com/v1/tournaments/results",
        "stage_id": "KOtwQCtI",
        "target_status": "FINISHED"
    },
    {
        "name": "Premier League 23/24",
        "url": "https://flashlive-sports.p.rapidapi.com/v1/tournaments/results",
        "stage_id": "SY30SsKF",
        "target_status": "FINISHED"
    },
    {
        "name": "FIFA Club World Cup (Play Offs)",
        "url": "https://flashlive-sports.p.rapidapi.com/v1/tournaments/results",
        "stage_id": "tvVoOjBU",
        "target_status": "FINISHED"
    },
    {
        "name": "World Cup 2026 (Fixtures)",
        "url": "https://flashlive-sports.p.rapidapi.com/v1/tournaments/fixtures",
        "stage_id": "SbLsX4y7",
        "target_status": "SCHEDULED"
    }
]

def get_or_create_team(team_id, team_name):
    """Ensures a team exists in the database to prevent foreign key violations."""
    team = session.query(Team).filter_by(team_id=team_id).first()
    if not team:
        team = Team(team_id=team_id, name=team_name)
        session.add(team)
        session.commit()
    return team

def execute_task(task):
    """Executes an individual scraping task with pagination and error handling."""
    name = task['name']
    url = task['url']
    stage_id = task['stage_id']
    target_status = task['target_status']
    
    page = 1
    total_added = 0
    
    print(f"\n--- Executing Task: {name} ---")
    print(f"Target Endpoint: {url}")
    
    while True:
        print(f"  -> Fetching Page {page}...")
        querystring = {"locale": "en_INT", "tournament_stage_id": stage_id, "page": str(page)}
        
        try:
            response = requests.get(url, headers=headers, params=querystring)
        except Exception as e:
            print(f"     [!] Network connection failure on page {page}: {e}. Skipping task.")
            break
            
        if response.status_code == 404:
            print(f"  -> Reached the end of available API pages (404). Task {name} complete.")
            break
        elif response.status_code != 200:
            print(f"     [!] API Exception {response.status_code}: {response.text}")
            break

        data = response.json()
        data_block = data.get('DATA', [])
        
        # Break condition: if the data block or events list is completely empty, pagination is complete
        if not data_block or not data_block[0].get('EVENTS'):
            print(f"  -> No further match objects returned. Task {name} complete.")
            break
            
        events = data_block[0].get('EVENTS', [])
        page_added = 0
        
        for event in events:
            # Enforce the specific match status for this task
            if event.get('STAGE_TYPE') != target_status:
                continue

            match_id = event['EVENT_ID']
            match_date = datetime.fromtimestamp(event['START_TIME'])
            
            # Extract team data
            home_id = event['HOME_PARTICIPANT_IDS'][0]
            home_name = event['HOME_NAME']
            
            away_id = event['AWAY_PARTICIPANT_IDS'][0]
            away_name = event['AWAY_NAME']

            
            home_score = event.get('HOME_SCORE_CURRENT')
            if home_score is not None: 
                home_score = int(home_score)
            
            away_score = event.get('AWAY_SCORE_CURRENT')
            if away_score is not None: 
                away_score = int(away_score)

            
            get_or_create_team(home_id, home_name)
            get_or_create_team(away_id, away_name)

        
            existing_match = session.query(Match).filter_by(match_id=match_id).first()
            if not existing_match:
                new_match = Match(
                    match_id=match_id,
                    home_team_id=home_id,
                    away_team_id=away_id,
                    match_date=match_date,
                    competition_name=name,
                    home_score=home_score,
                    away_score=away_score,
                    status=target_status
                )
                session.add(new_match)
                page_added += 1

        try:
            # Commit at the end of every page to preserve partial progress if an issue occurs later
            session.commit()
            total_added += page_added
            print(f"     [+] Successfully committed {page_added} matches from page {page}.")
        except Exception as e:
            session.rollback()
            print(f"     [!] Database exception saving page {page}: {e}")

        # Rate Limit Guard: 2 second pause between individual page updates
        time.sleep(2) 
        page += 1

    return total_added

if __name__ == "__main__":
    print("==================================================")
    print("STARTING DATA PIPELINE INGESTION RUNNER")
    print("==================================================")
    
    grand_total = 0
    
    for task in SCRAPING_TASKS:
        matches_saved = execute_task(task)
        grand_total += matches_saved
        # Cooldown period between heavy target endpoint transitions
        time.sleep(4) 
        
    print(f"\n==================================================")
    print("PIPELINE PROCESSING COMPLETE")
    print(f"Total new historical/scheduled records added: {grand_total}")
    print("==================================================")