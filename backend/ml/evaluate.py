import os
import sys
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, f1_score, precision_score, recall_score

sys.path.append(os.path.dirname(__file__))
from train import generate_synthetic_data

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
MODEL_PATH = os.path.join(MODEL_DIR, "ml_model.pkl")
PIPELINE_PATH = os.path.join(MODEL_DIR, "preprocess_pipeline.pkl")

def evaluate():
    if not os.path.exists(MODEL_PATH) or not os.path.exists(PIPELINE_PATH):
        raise FileNotFoundError("Model artifacts not found. Run train.py first.")

    model = joblib.load(MODEL_PATH)
    preprocessor = joblib.load(PIPELINE_PATH)

    df = generate_synthetic_data(800)
    X = df.drop(columns=["target", "approved"])
    y = df["approved"]

    X_transformed = preprocessor.transform(X)
    if hasattr(X_transformed, "toarray"):
        X_transformed = X_transformed.toarray()

    y_prob = model.predict_proba(X_transformed)[:, 1]
    y_pred = (y_prob >= 0.5).astype(int)

    return {
        "roc_auc": roc_auc_score(y, y_prob),
        "f1": f1_score(y, y_pred),
        "precision": precision_score(y, y_pred),
        "recall": recall_score(y, y_pred),
    }

if __name__ == "__main__":
    print(evaluate())
