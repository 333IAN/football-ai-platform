import subprocess
import sys
import datetime
import os

def run_pipeline():
    print("==================================================")
    print(f"AUTOMATED AI PIPELINE STARTED | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("==================================================")

    # Run the Data Ingestion Script
    print("\n[1/2] Checking API for new match results...")
    
    # We use sys.executable to ensure it uses your 'fap-env' virtual environment
    ingest_process = subprocess.run(
        [sys.executable, "mass_ingestion.py"], 
        capture_output=True, 
        text=True
    )
    
    # Print the output of the ingestion script so we can read it in the logs
    print(ingest_process.stdout)

    if ingest_process.returncode != 0:
        print("[!] FATAL ERROR during data ingestion. Halting pipeline.")
        print(ingest_process.stderr)
        return

    # If the ingestion script says 0 new records, we skip training to save CPU power
    if "Total new historical/scheduled records added: 0" in ingest_process.stdout:
        print("[*] No new matches found today. AI is already up to date. Skipping retraining.")
        print("==================================================")
        return

    # Retrain the XGBoost Model
    print("\n[2/2] New data found! Retraining XGBoost Model and recalculating Elo...")
    train_process = subprocess.run(
        [sys.executable, "train_model.py"], 
        capture_output=True, 
        text=True
    )
    
    print(train_process.stdout)

    if train_process.returncode != 0:
        print("[!] FATAL ERROR during model training.")
        print(train_process.stderr)
        return

    print("==================================================")
    print(f"PIPELINE SUCCESS | AI BRAIN UPDATED AT {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("==================================================")

if __name__ == "__main__":
    # Ensure the script runs in the directory where it's located
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    run_pipeline()