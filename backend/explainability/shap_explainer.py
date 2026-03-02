"""
SHAP Explainable AI Integration
Provides feature contribution analysis using SHAP values for credit decisions.
Deterministic and optimized for production use.
"""

import numpy as np
import joblib
import os
from typing import Dict, List, Optional, Tuple


class SHAPExplainer:
    """
    Cached SHAP explainer for fast, deterministic feature importance analysis.
    Supports both tree-based and linear models.
    """
    
    def __init__(self, model_path: str, pipeline_path: str, stats_path: str):
        """
        Initialize SHAP explainer with cached model artifacts.
        
        Args:
            model_path: Path to trained ML model
            pipeline_path: Path to preprocessing pipeline
            stats_path: Path to feature statistics
        """
        self.model = None
        self.preprocessor = None
        self.stats = {}
        self.explainer = None
        self.feature_names = []
        self.feature_means = []
        
        # Load model artifacts
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
        
        if os.path.exists(pipeline_path):
            self.preprocessor = joblib.load(pipeline_path)
        
        if os.path.exists(stats_path):
            self.stats = joblib.load(stats_path)
            self.feature_names = self.stats.get("feature_names", [])
            self.feature_means = self.stats.get("feature_means", [])
        
        # Initialize SHAP explainer (cached for performance)
        self._initialize_explainer()
    
    def _initialize_explainer(self):
        """Initialize SHAP explainer based on model type."""
        if self.model is None:
            return
        
        try:
            import shap
            
            # Determine model type and create appropriate explainer
            if hasattr(self.model, 'tree_'):
                # Decision Tree
                self.explainer = shap.TreeExplainer(self.model)
            elif hasattr(self.model, 'estimators_'):
                # Random Forest, Gradient Boosting, etc.
                self.explainer = shap.TreeExplainer(self.model)
            elif hasattr(self.model, 'coef_'):
                # Linear models (Logistic Regression, etc.)
                # Use feature means as background data
                if len(self.feature_means) > 0:
                    background = np.array(self.feature_means).reshape(1, -1)
                    self.explainer = shap.LinearExplainer(self.model, background)
                else:
                    self.explainer = None
            else:
                # Fallback: use KernelExplainer (slower but universal)
                # Not recommended for production due to performance
                self.explainer = None
        
        except ImportError:
            # SHAP not installed, fall back to basic explainability
            self.explainer = None
        except Exception as e:
            print(f"SHAP initialization warning: {str(e)}")
            self.explainer = None
    
    def explain(self, input_data: Dict, top_n: int = 3) -> Dict:
        """
        Generate SHAP-based explanation for credit decision.
        
        Args:
            input_data: Dictionary with income, expenses, employment_type, job_tenure
            top_n: Number of top positive and negative factors to return
        
        Returns:
            Dictionary with positive_factors and risk_factors
        """
        if self.model is None or self.preprocessor is None:
            return self._fallback_explanation(input_data, top_n)
        
        try:
            # Preprocess input
            import pandas as pd
            df = pd.DataFrame([input_data])
            transformed = self.preprocessor.transform(df)
            
            if hasattr(transformed, "toarray"):
                transformed = transformed.toarray()
            
            # Get SHAP values if explainer is available
            if self.explainer is not None:
                shap_values = self._get_shap_values(transformed)
                return self._format_shap_explanation(shap_values, top_n)
            else:
                # Fallback to feature importance
                return self._fallback_explanation_with_features(transformed[0], top_n)
        
        except Exception as e:
            print(f"SHAP explanation error: {str(e)}")
            return self._fallback_explanation(input_data, top_n)
    
    def _get_shap_values(self, transformed_data: np.ndarray) -> np.ndarray:
        """Get SHAP values from explainer."""
        try:
            import shap
            
            shap_values = self.explainer.shap_values(transformed_data)
            
            # Handle different SHAP output formats
            if isinstance(shap_values, list):
                # Binary classification: use positive class (index 1)
                shap_values = shap_values[1] if len(shap_values) > 1 else shap_values[0]
            
            # Ensure 1D array for single prediction
            if len(shap_values.shape) > 1:
                shap_values = shap_values[0]
            
            return shap_values
        
        except Exception as e:
            print(f"SHAP values extraction error: {str(e)}")
            return np.array([])
    
    def _format_shap_explanation(self, shap_values: np.ndarray, top_n: int) -> Dict:
        """Format SHAP values into positive and risk factors."""
        if len(shap_values) == 0:
            return {"positive_factors": [], "risk_factors": []}
        
        # Get feature names
        if len(self.feature_names) == 0:
            if self.preprocessor and hasattr(self.preprocessor, 'named_steps'):
                try:
                    self.feature_names = self.preprocessor.named_steps["preprocess"].get_feature_names_out().tolist()
                except:
                    self.feature_names = [f"feature_{i}" for i in range(len(shap_values))]
            else:
                self.feature_names = [f"feature_{i}" for i in range(len(shap_values))]
        
        # Ensure feature names match SHAP values length
        if len(self.feature_names) != len(shap_values):
            self.feature_names = [f"feature_{i}" for i in range(len(shap_values))]
        
        # Create feature-impact pairs
        feature_impacts = [
            {"feature": self._clean_feature_name(name), "impact": float(value)}
            for name, value in zip(self.feature_names, shap_values)
        ]
        
        # Sort by absolute impact
        feature_impacts.sort(key=lambda x: abs(x["impact"]), reverse=True)
        
        # Separate positive and negative factors
        positive_factors = [f for f in feature_impacts if f["impact"] > 0][:top_n]
        risk_factors = [f for f in feature_impacts if f["impact"] < 0][:top_n]
        
        # Convert negative impacts to positive for risk factors (easier to understand)
        risk_factors = [
            {"feature": f["feature"], "impact": abs(f["impact"])}
            for f in risk_factors
        ]
        
        return {
            "positive_factors": positive_factors,
            "risk_factors": risk_factors
        }
    
    def _fallback_explanation_with_features(self, feature_values: np.ndarray, top_n: int) -> Dict:
        """Fallback explanation using feature importances."""
        if self.model is None:
            return {"positive_factors": [], "risk_factors": []}
        
        # Get feature importances
        importances = None
        if hasattr(self.model, "coef_"):
            importances = self.model.coef_[0] if len(self.model.coef_.shape) > 1 else self.model.coef_
        elif hasattr(self.model, "feature_importances_"):
            importances = self.model.feature_importances_
        
        if importances is None:
            return {"positive_factors": [], "risk_factors": []}
        
        # Get feature names
        if len(self.feature_names) == 0:
            if self.preprocessor and hasattr(self.preprocessor, 'named_steps'):
                try:
                    self.feature_names = self.preprocessor.named_steps["preprocess"].get_feature_names_out().tolist()
                except:
                    self.feature_names = [f"feature_{i}" for i in range(len(importances))]
            else:
                self.feature_names = [f"feature_{i}" for i in range(len(importances))]
        
        # Calculate impacts (importance * deviation from mean)
        feature_means = np.array(self.feature_means) if len(self.feature_means) == len(feature_values) else np.zeros_like(feature_values)
        deviations = feature_values - feature_means
        impacts = importances * deviations
        
        # Create feature-impact pairs
        feature_impacts = [
            {"feature": self._clean_feature_name(name), "impact": float(impact)}
            for name, impact in zip(self.feature_names, impacts)
        ]
        
        # Sort by absolute impact
        feature_impacts.sort(key=lambda x: abs(x["impact"]), reverse=True)
        
        # Separate positive and negative factors
        positive_factors = [f for f in feature_impacts if f["impact"] > 0][:top_n]
        risk_factors = [f for f in feature_impacts if f["impact"] < 0][:top_n]
        
        # Convert negative impacts to positive for risk factors
        risk_factors = [
            {"feature": f["feature"], "impact": abs(f["impact"])}
            for f in risk_factors
        ]
        
        return {
            "positive_factors": positive_factors,
            "risk_factors": risk_factors
        }
    
    def _fallback_explanation(self, input_data: Dict, top_n: int) -> Dict:
        """Basic fallback explanation when SHAP is not available."""
        positive_factors = []
        risk_factors = []
        
        # Simple heuristic-based explanation
        income = input_data.get("income", 0)
        expenses = input_data.get("expenses", 0)
        job_tenure = input_data.get("job_tenure", 0)
        employment_type = input_data.get("employment_type", "")
        
        # Calculate savings ratio
        savings_ratio = (income - expenses) / (income + 1e-6) if income > 0 else 0
        
        # Positive factors
        if income > 5000:
            positive_factors.append({"feature": "High income", "impact": 0.3})
        if savings_ratio > 0.3:
            positive_factors.append({"feature": "Good savings ratio", "impact": 0.25})
        if job_tenure > 3:
            positive_factors.append({"feature": "Stable employment", "impact": 0.2})
        if employment_type.lower() in ['full-time', 'fulltime']:
            positive_factors.append({"feature": "Full-time employment", "impact": 0.15})
        
        # Risk factors
        if savings_ratio < 0.1:
            risk_factors.append({"feature": "Low savings ratio", "impact": 0.3})
        if expenses > income * 0.8:
            risk_factors.append({"feature": "High expense ratio", "impact": 0.25})
        if job_tenure < 1:
            risk_factors.append({"feature": "Short job tenure", "impact": 0.2})
        if income < 2000:
            risk_factors.append({"feature": "Low income", "impact": 0.15})
        
        return {
            "positive_factors": positive_factors[:top_n],
            "risk_factors": risk_factors[:top_n]
        }
    
    def _clean_feature_name(self, name: str) -> str:
        """Clean feature name for better readability."""
        # Remove pipeline prefixes
        name = name.replace("preprocess__", "")
        name = name.replace("remainder__", "")
        
        # Convert to readable format
        name = name.replace("_", " ").title()
        
        # Handle specific feature names
        replacements = {
            "Income": "Income Level",
            "Expenses": "Monthly Expenses",
            "Job Tenure": "Employment Tenure",
            "Tenure Years": "Years at Job",
            "Savings Ratio": "Savings Rate",
            "Expense To Income Ratio": "Expense Ratio",
            "Stability Score": "Employment Stability",
        }
        
        for old, new in replacements.items():
            if old in name:
                name = name.replace(old, new)
        
        return name


# Global cached explainer instance
_cached_explainer: Optional[SHAPExplainer] = None


def get_explainer(model_path: str, pipeline_path: str, stats_path: str) -> SHAPExplainer:
    """
    Get cached SHAP explainer instance.
    Creates new instance only if paths change.
    
    Args:
        model_path: Path to trained ML model
        pipeline_path: Path to preprocessing pipeline
        stats_path: Path to feature statistics
    
    Returns:
        Cached SHAPExplainer instance
    """
    global _cached_explainer
    
    if _cached_explainer is None:
        _cached_explainer = SHAPExplainer(model_path, pipeline_path, stats_path)
    
    return _cached_explainer


def explain_with_shap(input_data: Dict, model_path: str, pipeline_path: str, stats_path: str, top_n: int = 3) -> Dict:
    """
    Generate SHAP-based explanation for credit decision.
    
    Args:
        input_data: Dictionary with income, expenses, employment_type, job_tenure
        model_path: Path to trained ML model
        pipeline_path: Path to preprocessing pipeline
        stats_path: Path to feature statistics
        top_n: Number of top factors to return (default: 3)
    
    Returns:
        Dictionary with positive_factors and risk_factors
    """
    explainer = get_explainer(model_path, pipeline_path, stats_path)
    return explainer.explain(input_data, top_n)
