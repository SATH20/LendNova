import os
import sys
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, f1_score, precision_score, recall_score

sys.path.append(os.path.dirname(__file__))
from feature_engineering import FeatureEngineer

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODEL_DIR, "ml_model.pkl")
PIPELINE_PATH = os.path.join(MODEL_DIR, "preprocess_pipeline.pkl")
FEATURE_STATS_PATH = os.path.join(MODEL_DIR, "feature_stats.pkl")

def generate_synthetic_data(n_samples=2000):
    rng = np.random.default_rng(42)

    incomes = rng.lognormal(mean=8.5, sigma=0.8, size=n_samples)
    expenses = incomes * rng.uniform(0.3, 0.9, size=n_samples)
    tenure = rng.exponential(scale=3.0, size=n_samples)

    employment_types = rng.choice(
        ["Full-time", "Part-time", "Self-employed", "Unemployed", "Student"],
        size=n_samples,
        p=[0.6, 0.15, 0.15, 0.05, 0.05],
    )

    df = pd.DataFrame(
        {
            "income": incomes,
            "expenses": expenses,
            "job_tenure": tenure,
            "employment_type": employment_types,
        }
    )

    risk_score = (
        (df["expenses"] / (df["income"] + 1)) * 50
        + (1 / (df["job_tenure"] + 1)) * 20
        + rng.normal(0, 10, size=n_samples)
    )

    employment_risk = {
        "Full-time": -10,
        "Self-employed": 0,
        "Part-time": 10,
        "Student": 20,
        "Unemployed": 30,
    }

    risk_score += df["employment_type"].map(employment_risk)
    threshold = np.percentile(risk_score, 80)
    df["target"] = (risk_score > threshold).astype(int)
    df["approved"] = 1 - df["target"]

    return df

def build_preprocessor():
    numeric_features = [
        "income",
        "expenses",
        "job_tenure",
        "tenure_years",
        "savings_ratio",
        "expense_to_income_ratio",
        "stability_score",
    ]
    categorical_features = ["employment_type"]

    numeric_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    transformer = ColumnTransformer(
        [
            ("num", numeric_pipeline, numeric_features),
            ("cat", categorical_pipeline, categorical_features),
        ]
    )

    return Pipeline(
        [
            ("engineer", FeatureEngineer()),
            ("preprocess", transformer),
        ]
    )

def evaluate_pipeline(pipeline, X_train, y_train, X_test, y_test):
    pipeline.fit(X_train, y_train)
    y_prob = pipeline.predict_proba(X_test)[:, 1]
    y_pred = (y_prob >= 0.5).astype(int)

    return {
        "roc_auc": roc_auc_score(y_test, y_prob),
        "f1": f1_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
    }

def train_models():
    df = generate_synthetic_data(2400)
    X = df.drop(columns=["target", "approved"])
    y = df["approved"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    candidates = {
        "Logistic Regression": LogisticRegression(max_iter=400),
        "Random Forest": RandomForestClassifier(n_estimators=180, random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=200, random_state=42),
    }

    best_name = None
    best_score = -1
    best_pipeline = None

    for name, model in candidates.items():
        preprocessor = build_preprocessor()
        pipeline = Pipeline(
            [
                ("preprocess", preprocessor),
                ("model", model),
            ]
        )
        cv_scores = cross_val_score(
            pipeline, X_train, y_train, cv=5, scoring="roc_auc"
        )
        metrics = evaluate_pipeline(pipeline, X_train, y_train, X_test, y_test)
        roc_auc = metrics["roc_auc"]
        if roc_auc > best_score:
            best_score = roc_auc
            best_name = name
            best_pipeline = pipeline

    best_pipeline.fit(X, y)
    fitted_preprocessor = best_pipeline.named_steps["preprocess"]
    fitted_model = best_pipeline.named_steps["model"]

    transformed = fitted_preprocessor.transform(X)
    if hasattr(transformed, "toarray"):
        transformed = transformed.toarray()
    feature_names = (
        fitted_preprocessor.named_steps["preprocess"].get_feature_names_out().tolist()
    )
    feature_means = np.mean(transformed, axis=0).tolist()

    joblib.dump(fitted_model, MODEL_PATH)
    joblib.dump(fitted_preprocessor, PIPELINE_PATH)
    joblib.dump(
        {"feature_names": feature_names, "feature_means": feature_means, "model": best_name},
        FEATURE_STATS_PATH,
    )

    return {"model": best_name, "roc_auc": best_score}

if __name__ == "__main__":
    train_models()
