from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import numpy as np
import pickle
import logging
from datetime import datetime
import uvicorn
import os

# ---------------------------------------------
# Logging Setup
# ---------------------------------------------
logging.basicConfig(
    filename="requests.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI()

# ---------------------------------------------
# Load model & encoders (RELATIVE PATHS FOR DOCKER)
# ---------------------------------------------
model = None
encoders = None

try:
    model_path = os.path.join("source", "model_xgb.pkl")
    enc_path = os.path.join("source", "encoders.pkl")

    model = pickle.load(open(model_path, "rb"))
    encoders = pickle.load(open(enc_path, "rb"))

    logging.info("Model & encoders loaded successfully")
except Exception as e:
    logging.error(f"Error loading model/encoders: {e}")

# ---------------------------------------------
# Home page
# ---------------------------------------------
@app.get("/")
def home():
    try:
        with open("index.html", "r") as f:
            return HTMLResponse(f.read())
    except Exception as e:
        logging.error(f"Error loading index.html: {e}")
        return {"error": "index.html not found"}

# ---------------------------------------------
# SIMPLE TEST ENDPOINT
# ---------------------------------------------
@app.get("/test")
def test():
    return {"message": "API is working"}

# ---------------------------------------------
# Prediction Endpoint
# ---------------------------------------------
@app.get("/predict")
def predict(
    amount: float,
    transaction_type: str,
    channel: str,
    geo_location: str,
    transaction_velocity_1h: int,
    transaction_velocity_24h: int,
    avg_spend_7d: float,
    customer_risk_score: float,
    account_age_days: int,
    card_present: int,
    international_flag: int,
    previous_fraud_history: int,
    merchant_category: str
):

    if model is None or encoders is None:
        return {"error": "Model or encoders not loaded"}

    try:
        # Encode categorical values
        t_type = encoders["transaction_type"].transform([transaction_type])[0]
        channel_enc = encoders["channel"].transform([channel])[0]
        location = encoders["geo_location"].transform([geo_location])[0]
        m_cat = encoders["merchant_category"].transform([merchant_category])[0]

        # Auto time features
        now = datetime.now()
        hour, day, month = now.hour, now.day, now.month

        # Build feature array
        final = np.array([
            amount,
            t_type,
            channel_enc,
            location,
            transaction_velocity_1h,
            transaction_velocity_24h,
            avg_spend_7d,
            customer_risk_score,
            account_age_days,
            card_present,
            international_flag,
            previous_fraud_history,
            m_cat,
            hour, day, month
        ]).reshape(1, -1)

        pred = model.predict(final)[0]
        result = "Fraud" if pred == 1 else "Not Fraud"

        return {"prediction": result}

    except Exception as e:
        logging.error(f"Prediction error: {e}")
        return {"error": str(e)}

# ---------------------------------------------
# LOCAL RUN
# ---------------------------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
