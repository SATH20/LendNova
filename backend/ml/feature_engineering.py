import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

class FeatureEngineer(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()
        
        # Ensure correct types
        X['income'] = pd.to_numeric(X['income'], errors='coerce').fillna(0)
        X['expenses'] = pd.to_numeric(X['expenses'], errors='coerce').fillna(0)
        X['job_tenure'] = pd.to_numeric(X['job_tenure'], errors='coerce').fillna(0)
        
        # Create derived features
        X['savings_ratio'] = (X['income'] - X['expenses']) / (X['income'] + 1e-6)
        X['expense_to_income_ratio'] = X['expenses'] / (X['income'] + 1e-6)
        
        # Stability score based on tenure
        X['stability_score'] = np.log1p(X['job_tenure']) * 10
        
        # Categorical Encoding (Simple mapping for this demo, usually OneHotEncoder in pipeline)
        employment_map = {
            'Full-time': 5,
            'Self-employed': 4, 
            'Part-time': 3,
            'Student': 2,
            'Unemployed': 1
        }
        X['employment_encoded'] = X['employment_type'].map(employment_map).fillna(1)
        
        return X[['income', 'expenses', 'job_tenure', 'savings_ratio', 'expense_to_income_ratio', 'stability_score', 'employment_encoded']]
