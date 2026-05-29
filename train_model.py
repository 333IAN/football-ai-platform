import pandas as pd
import joblib
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import xgboost as xgb

# 1. Connect to PostgreSQL
load_dotenv()
DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DATABASE_URL)

def load_data():
    print("Pulling historical match data from PostgreSQL...")
    query = """
        SELECT home_team_id, away_team_id, home_score, away_score 
        FROM matches 
        WHERE status = 'FINISHED' AND home_score IS NOT NULL AND away_score IS NOT NULL
    """
    df = pd.read_sql(query, engine)
    return df

def engineer_features(df):
    print("Engineering features and target variables...")
    # Create the Target Variable: 2 = Home Win, 1 = Draw, 0 = Away Win
    conditions = [
        (df['home_score'] > df['away_score']),
        (df['home_score'] == df['away_score']),
        (df['home_score'] < df['away_score'])
    ]
    choices = [2, 1, 0]
    import numpy as np
    df['target'] = np.select(conditions, choices, default=1)

    # Machine learning models only understand numbers. We must encode the string Team IDs.
    le = LabelEncoder()
    
    # Combine home and away IDs to ensure the encoder learns all possible teams
    all_teams = pd.concat([df['home_team_id'], df['away_team_id']])
    le.fit(all_teams)

    df['home_team_encoded'] = le.transform(df['home_team_id'])
    df['away_team_encoded'] = le.transform(df['away_team_id'])

    # Save the encoder so our API knows how to translate team names later!
    joblib.dump(le, 'ml_models/saved_models/team_encoder.pkl')

    # Drop the columns we don't need for training
    features = df[['home_team_encoded', 'away_team_encoded']]
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
        X, y = engineer_features(df)
        trained_model = train_and_evaluate(X, y)
        
        # Save the trained model to disk
        model_path = 'ml_models/saved_models/xgboost_baseline.pkl'
        joblib.dump(trained_model, model_path)
        print(f"\nSuccess! Model saved to {model_path}")