import pandas as pd
import numpy as np

def explain_decision(model, features, top_n=5):
    """
    Extracts feature importance from the model and returns top influencing factors.
    """
    try:
        if hasattr(model, 'coef_'):
            # Linear Model
            importances = model.coef_[0]
            feature_names = features.columns
        elif hasattr(model, 'feature_importances_'):
            # Tree Model
            importances = model.feature_importances_
            feature_names = features.columns
        else:
            return [{"factor": "Model Default", "impact": 0.5}]
            
        factors = []
        for name, imp in zip(feature_names, importances):
            factors.append({
                "factor": name,
                "impact": float(imp)
            })
            
        # Sort by absolute impact
        factors.sort(key=lambda x: abs(x['impact']), reverse=True)
        return factors[:top_n]
        
    except Exception as e:
        print(f"Explainability Error: {str(e)}")
        return [{"factor": "Unknown", "impact": 0.0}]
