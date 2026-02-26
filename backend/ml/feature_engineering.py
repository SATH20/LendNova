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

        X['income'] = pd.to_numeric(X['income'], errors='coerce').fillna(0)
        X['expenses'] = pd.to_numeric(X['expenses'], errors='coerce').fillna(0)
        X['job_tenure'] = pd.to_numeric(X['job_tenure'], errors='coerce').fillna(0)

        X['savings_ratio'] = (X['income'] - X['expenses']) / (X['income'] + 1e-6)
        X['expense_to_income_ratio'] = X['expenses'] / (X['income'] + 1e-6)

        X['tenure_years'] = X['job_tenure']
        X['stability_score'] = np.log1p(X['tenure_years']) * 10

        return X[['income', 'expenses', 'job_tenure', 'tenure_years', 'savings_ratio', 'expense_to_income_ratio', 'stability_score', 'employment_type']]
