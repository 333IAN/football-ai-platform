import os
import pickle
import pandas as pd
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session, sessionmaker
from database_setup import engine, Team

# 1. Initialize FastAPI App
app = FastAPI(
    title="Football AI Prediction Engine",
    description="Production API serving real-time match outcome probabilities.",
    version="1.0.0"
)

# 2. Enable CORS (Crucial for connecting your React frontend later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, swap this for your specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Database Session Dependency
SessionLocal = sessionmaker(bind=engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 4. Load the Trained XGBoost Model Safely
MODEL_PATH = "ml_models/saved_models/xgboost_baseline.pkl"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"[!] Model file '{MODEL_PATH}' not found. Please run train_model.py first.")

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

# 5. Define Pydantic Request Schema
class PredictionRequest(BaseModel):
    home_team_id: str
    away_team_id: str

# 6. API Endpoints
@app.get("/")
def health_check():
    return {"status": "online", "model_loaded": True, "accuracy_baseline": "60.00%"}

@app.get("/teams")
def get_all_teams(db: Session = Depends(get_db)):
    """
    Retrieves a list of all teams currently stored in the database 
    along with their unique IDs and current Elo ratings.
    """
    teams = db.query(Team).all()
    return [
        {
            "team_id": team.team_id,
            "name": team.name,
            "current_elo": getattr(team, 'current_elo', 1500.0) or 1500.0
        }
        for team in teams
    ]

@app.post("/predict")
def predict_match_outcome(request: PredictionRequest, db: Session = Depends(get_db)):
    """
    Accepts two team IDs, fetches their current Elo ratings from PostgreSQL,
    and runs them through the XGBoost model to generate probabilities.
    """
    # Fetch team data from the database
    home_team = db.query(Team).filter_by(team_id=request.home_team_id).first()
    away_team = db.query(Team).filter_by(team_id=request.away_team_id).first()

    if not home_team or not away_team:
        raise HTTPException(
            status_code=404, 
            detail=f"One or both teams not found. Home Exist: {bool(home_team)}, Away Exist: {bool(away_team)}"
        )

    # Fallback to a baseline Elo if a team exists but has no rating calculated yet
    home_elo = getattr(home_team, 'current_elo', 1500.0) or 1500.0
    away_elo = getattr(away_team, 'current_elo', 1500.0) or 1500.0

    # Format the input data to exactly match the training DataFrame structure
    input_data = pd.DataFrame([{
        'home_elo_before': home_elo,
        'away_elo_before': away_elo
    }])

    try:
        # Generate raw probabilities for [Away Win, Draw, Home Win] or your model's specific classes
        probabilities = model.predict_proba(input_data)[0]
        prediction = int(model.predict(input_data)[0])
        
        # Adjust mapping labels depending on how your label encoder ordered your target values (0, 1, 2)
        return {
            "home_team": home_team.name,
            "away_team": away_team.name,
            "home_elo": home_elo,
            "away_elo": away_elo,
            "prediction_class": prediction,
            "probabilities": {
                "away_win_prob": round(float(probabilities[0]), 4),
                "draw_prob": round(float(probabilities[1]), 4),
                "home_win_prob": round(float(probabilities[2]), 4)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction Engine Failure: {str(e)}")