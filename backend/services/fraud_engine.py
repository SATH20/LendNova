import numpy as np
from datetime import date
from sklearn.ensemble import IsolationForest
from utils.helpers import parse_date

_iso_model = None

def _get_isolation_model():
    global _iso_model
    if _iso_model is not None:
        return _iso_model

    rng = np.random.default_rng(7)
    incomes = rng.lognormal(mean=8.5, sigma=0.8, size=1200)
    expenses = incomes * rng.uniform(0.3, 0.9, size=1200)
    tenure = rng.exponential(scale=3.0, size=1200)
    ratio = expenses / (incomes + 1)

    X_train = np.column_stack([incomes, expenses, tenure, ratio])
    _iso_model = IsolationForest(contamination=0.05, random_state=42)
    _iso_model.fit(X_train)
    return _iso_model

def detect_fraud(form_data, ocr_data):
    flags = []

    income_claimed = float(form_data.get("income", 0) or 0)
    expenses_claimed = float(form_data.get("expenses", 0) or 0)
    tenure_claimed = float(form_data.get("job_tenure", 0) or 0)
    income_ocr = ocr_data.get("income")

    if income_ocr is not None:
        diff = abs(income_claimed - income_ocr)
        if diff > max(150, income_claimed * 0.12):
            flags.append("Income mismatch beyond tolerance")

    name_input = (ocr_data.get("name") or "").strip().lower()
    if name_input and len(name_input.split()) < 2:
        flags.append("Name extraction incomplete")

    raw_text = (ocr_data.get("raw_text") or ocr_data.get("extracted_text") or "").lower()
    if "exp" in raw_text:
        expiry = parse_date(raw_text)
        if expiry and expiry.date() < date.today():
            flags.append("Document appears expired")

    if raw_text and max([len(chunk) for chunk in raw_text.split()]) > 40:
        flags.append("Suspicious formatting detected")

    ratio = expenses_claimed / (income_claimed + 1)
    model = _get_isolation_model()
    sample = np.array([[income_claimed, expenses_claimed, tenure_claimed, ratio]])
    score = model.score_samples(sample)[0]
    anomaly_prob = float(1 / (1 + np.exp(5 * score)))

    fraud_probability = min(1.0, anomaly_prob + 0.08 * len(flags))

    return {"fraud_probability": round(fraud_probability, 4), "flags": flags}
