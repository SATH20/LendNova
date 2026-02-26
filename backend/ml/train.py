import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.preprocessing import StandardScaler
from feature_engineering import FeatureEngineer

# Ensure models directory exists
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

def generate_synthetic_data(n_samples=1000):
    np.random.seed(42)
    
    incomes = np.random.lognormal(mean=8.5, sigma=0.8, size=n_samples)
    expenses = incomes * np.random.uniform(0.3, 0.9, size=n_samples)
    tenure = np.random.exponential(scale=3.0, size=n_samples)
    
    employment_types = np.random.choice(
        ['Full-time', 'Part-time', 'Self-employed', 'Unemployed', 'Student'],
        size=n_samples,
        p=[0.6, 0.15, 0.15, 0.05, 0.05]
    )
    
    df = pd.DataFrame({
        'income': incomes,
        'expenses': expenses,
        'job_tenure': tenure,
        'employment_type': employment_types
    })
    
    # Generate Target (Default Risk)
    # Rules: High expense ratio, low tenure, unemployed -> Higher Risk (Target=1)
    
    risk_score = (
        (df['expenses'] / (df['income'] + 1)) * 50 + 
        (1 / (df['job_tenure'] + 1)) * 20 + 
        np.random.normal(0, 10, size=n_samples)
    )
    
    # Adjust for employment type manually
    employment_risk = {
        'Full-time': -10,
        'Self-employed': 0,
        'Part-time': 10,
        'Student': 20,
        'Unemployed': 30
    }
    
    risk_score += df['employment_type'].map(employment_risk)
    
    # Threshold for target (1 = default, 0 = repay)
    # Let's say top 20% risk score are defaulters
    threshold = np.percentile(risk_score, 80)
    df['target'] = (risk_score > threshold).astype(int)
    
    # Invert for "Approval" (1 = Approve, 0 = Reject/Default)
    # So if target was default (1), approval is 0
    df['approved'] = 1 - df['target']
    
    return df

def train_models():
    print("Generating synthetic data...")
    df = generate_synthetic_data(2000)
    
    X = df.drop(['target', 'approved'], axis=1)
    y = df['approved']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Define Pipelines
    pipelines = {
        'Logistic Regression': Pipeline([
            ('engineer', FeatureEngineer()),
            ('scaler', StandardScaler()),
            ('model', LogisticRegression())
        ]),
        'Random Forest': Pipeline([
            ('engineer', FeatureEngineer()),
            ('model', RandomForestClassifier(n_estimators=100, random_state=42))
        ]),
        'Gradient Boosting': Pipeline([
            ('engineer', FeatureEngineer()),
            ('model', GradientBoostingClassifier(n_estimators=100, random_state=42))
        ])
    }
    
    best_score = 0
    best_model_name = ""
    best_pipeline = None
    
    print("\nTraining models...")
    for name, pipe in pipelines.items():
        pipe.fit(X_train, y_train)
        score = pipe.score(X_test, y_test)
        print(f"{name} Accuracy: {score:.4f}")
        
        if score > best_score:
            best_score = score
            best_model_name = name
            best_pipeline = pipe
            
    print(f"\nBest Model: {best_model_name} with Accuracy: {best_score:.4f}")
    
    # Save Model
    model_path = os.path.join(MODEL_DIR, 'ml_model.pkl')
    joblib.dump(best_pipeline, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_models()
