import time
import requests
from sqlalchemy.orm import sessionmaker
from database_setup import engine, Match, Team


Session = sessionmaker(bind=engine)
session = Session()

API_URL = "http://127.0.0.1:8000/predict"

def generate_bulk_forecasts():
    print("==================================================")
    print("        WORLD CUP 2026 BATCH FORECASTER")
    print("==================================================")
    
    # Query database for scheduled World Cup fixtures
    # Filtering by name contains 'World Cup 2026' to catch the exact string stored by mass_ingestion.py
    upcoming_matches = (
        session.query(Match)
        .filter(Match.competition_name.like("%World Cup 2026%"))
        .filter(Match.status == "SCHEDULED")
        .order_by(Match.match_date)
        .all()
    )
    
    if not upcoming_matches:
        print("No scheduled World Cup 2026 fixtures found in the database.")
        print("Please ensure mass_ingestion.py has been run successfully.")
        return

    print(f"[+] Found {len(upcoming_matches)} upcoming fixtures to evaluate.")
    print("-" * 75)
    print(f"{'DATE':<12} | {'HOME TEAM':<20} | {'AWAY TEAM':<20} | {'PREDICTION':<12}")
    print("-" * 75)

    success_count = 0
    
    for match in upcoming_matches:
        # Fetch names for logging purposes
        home_team = session.query(Team).filter_by(team_id=match.home_team_id).first()
        away_team = session.query(Team).filter_by(team_id=match.away_team_id).first()
        
        home_name = home_team.name if home_team else match.home_team_id
        away_name = away_team.name if away_team else match.away_team_id
        match_date_str = match.match_date.strftime("%Y-%m-%d")

        # Build payload for FastAPI endpoint
        payload = {
            "home_team_id": match.home_team_id,
            "away_team_id": match.away_team_id
        }

        try:
            response = requests.post(API_URL, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                probs = data.get("raw_mapped_probabilities", {})
                
                if probs:
                    best_class = max(probs, key=probs.get)
                    highest_prob = probs[best_class]
                    label_map={"2":"AWAY_WIN", "1":"HOME_WIN", "0":"DRAW"}
                    human_label=label_map.get(str(best_class), "UNKNOWN")
                    pick = f"{human_label} ({highest_prob*100:.1f}%)"
                else:
                    pick = "UNKNOWN"
                
                print(f"{match_date_str:<12} | {home_name:<20} | {away_name:<20} | {pick:<12}")
                success_count += 1
            else:
                print(f"{match_date_str:<12} | {home_name:<20} | {away_name:<20} | [!] API Error {response.status_code}")
        
        except requests.exceptions.ConnectionError:
            print("\n Critical Error: Unable to connect to the FastAPI server.")
            print("    Make sure your server is running via: uvicorn api:app --reload")
            break
        except Exception as e:
            print(f"{match_date_str:<12} | {home_name:<20} | {away_name:<20} | [!] Failed: {e}")
            
        time.sleep(0.1)

    print("-" * 75)
    print(f"BATCH PROCESSING COMPLETE: Generated {success_count}/{len(upcoming_matches)} forecasts.")
    print("==================================================")

if __name__ == "__main__":
    generate_bulk_forecasts()