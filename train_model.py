import pandas as pd
import joblib
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import xgboost as xgb
import numpy as np


# 1. Connect to PostgreSQL
load_dotenv()
DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DATABASE_URL)

def load_data():
    print("Pulling historical match data from PostgreSQL...")
    query = """
        SELECT home_team_id, away_team_id, home_score, away_score, match_date
        FROM matches 
        WHERE status = 'FINISHED' AND home_score IS NOT NULL AND away_score IS NOT NULL
        ORDER BY match_date ASC
    """
    df = pd.read_sql(query, engine)
    return df

def calculate_elo(df, k_factor=30):
    print("Computing dynamic Elo ratings...")
    elo_dict={}
    home_elos_before=[]
    away_elos_before=[]

    for index, row in df.iterrows():
        home=row['home_team_id']
        away=row['away_team_id']

        if home not in elo_dict: elo_dict[home]=1500.0
        if away not in elo_dict: elo_dict[away]=1500.0

        current_home_elo=elo_dict[home]
        current_away_elo=elo_dict[away]
        home_elos_before.append(current_home_elo)
        away_elos_before.append(current_away_elo)

        expected_home=1/(1+10 ** ((current_away_elo-current_home_elo)/400))
        expected_away=1/(1+10 ** ((current_home_elo-current_away_elo)/400))

        if row['home_score']>row['away_score']:
            actual_home, actual_away=1,0
        elif row['home_score']==row['away_score']:
            actual_home, actual_away=0.5, 0.5
        else:
            actual_home, actual_away=0, 1

        elo_dict[home]=current_home_elo+ k_factor * (actual_home-expected_home)
        elo_dict[away]=current_away_elo+ k_factor * (actual_away-expected_away)

    df['home_elo_before']=home_elos_before
    df['away_elo_before']=away_elos_before

    joblib.dump(elo_dict, 'ml_models/saved_models/current_elos.pkl')

    return df



def engineer_features(df):
    print("Engineering features and target variables...")
    # Create the Target Variable: 2 = Home Win, 1 = Draw, 0 = Away Win
    conditions = [
        (df['home_score'] > df['away_score']),
        (df['home_score'] == df['away_score']),
        (df['home_score'] < df['away_score'])
    ]
    df['target']=np.select(conditions, [2,1,0], default=1)

    features = df[['home_elo_before', 'away_elo_before']]
    target = df['target']
    
    return features, target

def train_and_evaluate(X, y):
    print("Splitting data and training XGBoost model...")
    # Split into 80% training data, 20% testing data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize the XGBoost Classifier
    model = xgb.XGBClassifier(
        objective='multi:softprob', 
        num_class=3, 
        eval_metric='mlogloss',
        seed=42
    )

    # Train the model
    model.fit(X_train, y_train)

    # Evaluate the model
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    
    print(f"\n--- Model Evaluation ---")
    print(f"Accuracy: {accuracy * 100:.2f}%\n")
    print("Classification Report:")
    print(classification_report(y_test, predictions, target_names=['Away Win', 'Draw', 'Home Win']))

    return model

if __name__ == "__main__":
    # Execute the pipeline
    df = load_data()
    
    if len(df) < 10:
        print("Not enough data to train a model. Check your database!")
    else:
        df_with_elo=calculate_elo(df)
        X, y = engineer_features(df_with_elo)
        trained_model = train_and_evaluate(X, y)
        
        # Save the trained model to disk
        model_path = 'ml_models/saved_models/xgboost_baseline.pkl'
        joblib.dump(trained_model, model_path)
        print(f"\nSuccess! Model saved to {model_path}")