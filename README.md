# ⚽ Football AI Prediction Platform

[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Google Cloud](https://img.shields.io/badge/GoogleCloud-%234285F4.svg?style=for-the-badge&logo=google-cloud&logoColor=white)](https://cloud.google.com/)
[![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com/)

A fully decoupled, serverless Machine Learning application that predicts the outcomes of professional football matches using historical data, dynamic Elo ratings, and an XGBoost classification engine.

![App Screenshot](/assets/mainscreenshot.png)

## 🧠 The Architecture

This project is built using a modern, scalable enterprise cloud architecture:

* **Frontend (The Face):** A responsive, dark-mode **React.js** dashboard built with **Vite** and **Tailwind CSS**. Hosted in a Dockerized Nginx container on **Google Cloud Run**.
* **Backend (The Engine):** A lightning-fast **FastAPI** Python server that serves the machine learning model via RESTful endpoints. Hosted on **Google Cloud Run** for auto-scaling.
* **Database (The Memory):** A **PostgreSQL** database hosted on **Supabase**, utilizing connection pooling for high availability.
* **Machine Learning (The Brain):** An **XGBoost** model trained on thousands of historical matches (ingested via the API-Football RapidAPI). The model calculates real-time **Elo Ratings** for every team before generating Home Win / Draw / Away Win probabilities.

---

## ⚙️ Features

* **Automated Data Pipeline:** A custom Python scraper (`mass_ingestion.py`) that feeds historical and scheduled match data into the cloud database.
* **Dynamic Elo Rating System:** Unlike static stats, the platform calculates fluid Elo ratings that adjust based on team momentum and opponent difficulty.
* **Live AI Inference:** The FastAPI backend loads the serialized `.pkl` models into memory and serves predictions with sub-second latency.
* **"Set & Forget" Updater:** Includes `auto_updater.py` to fetch daily match results, automatically retrain the ML model, and update the "brain" dynamically.

---

## 🚀 Local Development Setup

Want to run this locally? Follow these steps:

**1. Clone the repository**
```bash
git clone [https://github.com/333IAN/football-ai-platform.git](https://github.com/333IAN/football-ai-platform.git)
cd football-ai-platform
```

**2. Create and Activate Virtual Environment**
```bash
python3 -m venv fap-env
```
### Activate fap-env:
```bash
source fap-env/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Database Setup**
Create a free account on [Supabase](https://supabase.com) and create a new PostgreSQL database.
Get your connection string (ensure you use the IPv4 pooler string, usually port `6543`).
Create a `.env` file in the root directory:
   ```env
   DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@[aws-0-region.pooler.supabase.com:6543/postgres](https://aws-0-region.pooler.supabase.com:6543/postgres)
   API_FOOTBALL_KEY=[YOUR-RAPIDAPI-KEY]
   ```

**5. Database schema**
```bash
python database_setup.py
```

**6.ML Pipeline**
```bash
python mass_ingestion.py
```

**7. Train AI model**
```bash
python train_model.py
```

**8. Start backend server**
```bash
uvicorn api:app --reload --host 127.0.0.1 --port 8000
```

**9.Start frontend server**
```bash
cd frontend
npm install
npm run dev
```
### ☁️Cloud Deployment:
This application is fully Dockerized for Google Cloud Run.
* Backend is deployed from the root `Dockerfile`
* Frontend is deployed from `frontend/Dockerfile` and requires a `.env.production` file containing the `VITE_API_URL` of the live FASTAPI backend.

### 🤝Connect:
* Built by Ian Isavwa. Feel free to connect with me on [LinkedIn](https://www.linkedin.com/in/ian-isavwa-0510b9385) to discuss Data Science, Full-Stack Engineering, or why the AI keeps predicting Arsenal to lose🙂