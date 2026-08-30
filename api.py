import os
import pickle
import pandas as pd
import joblib  
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session, sessionmaker
from database_setup import engine, Team


app = FastAPI(
    title="Football AI Prediction Engine",
    version="1.1.0"
)

origins=[
    "https://football-ai-platform-frontend-888912540039.europe-west2.run.app",
    "https://localhost:5173",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


SessionLocal = sessionmaker(bind=engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


MODEL_PATH = "ml_models/saved_models/xgboost_baseline.pkl"
ELO_PATH = "ml_models/saved_models/current_elos.pkl"

if not os.path.exists(MODEL_PATH) or not os.path.exists(ELO_PATH):
    raise FileNotFoundError("[!] Missing critical ML artifacts. Run train_model.py first.")

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

elo_dict = joblib.load(ELO_PATH)

class PredictionRequest(BaseModel):
    home_team_id: str
    away_team_id: str

@app.get("/")
def health_check():
    return {"status": "online", "tracked_teams_with_elo": len(elo_dict)}

@app.get("/teams")
def get_all_teams(db: Session = Depends(get_db)):
    """
    Retrieves a list of all teams currently stored in the database.
    """
    teams = db.query(Team).order_by(Team.name).all()
    return [
        {
            "team_id": team.team_id,
            "name": team.name,
            "current_elo": elo_dict.get(team.team_id, 1500.0)
        }
        for team in teams
    ]

@app.post("/predict")
def predict_match_outcome(request: PredictionRequest, db: Session = Depends(get_db)):
    home_team = db.query(Team).filter_by(team_id=request.home_team_id).first()
    away_team = db.query(Team).filter_by(team_id=request.away_team_id).first()

    if not home_team or not away_team:
        raise HTTPException(status_code=404, detail="Teams not found.")

    home_elo = elo_dict.get(request.home_team_id, 1500.0)
    away_elo = elo_dict.get(request.away_team_id, 1500.0)

    input_data = pd.DataFrame([{
        'home_elo_before': home_elo,
        'away_elo_before': away_elo
    }])

    try:
        probabilities = model.predict_proba(input_data)[0]
        prediction = model.predict(input_data)[0]
        
        # DYNAMIC MAPPING: Create a dictionary matching actual model classes to probabilities
        # This handles strings ('HOME_WIN', 'DRAW') or encoded integers (0, 1, 2) perfectly
        class_probs = {str(cls): float(prob) for cls, prob in zip(model.classes_, probabilities)}
        
        return {
            "home_team": home_team.name,
            "away_team": away_team.name,
            "home_elo": round(home_elo, 1),
            "away_elo": round(away_elo, 1),
            "prediction_class": str(prediction),
            "raw_mapped_probabilities": class_probs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))