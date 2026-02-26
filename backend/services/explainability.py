import numpy as np

def explain_decision(model, feature_names, feature_values, feature_means, top_n=5):
    if feature_names is None or feature_values is None:
        return []

    importances = None
    if hasattr(model, "coef_"):
        importances = model.coef_[0]
    elif hasattr(model, "feature_importances_"):
        importances = model.feature_importances_

    if importances is None:
        return []

    feature_values = np.array(feature_values)
    if feature_means is None or len(feature_means) != len(feature_values):
        feature_means = np.zeros_like(feature_values)
    else:
        feature_means = np.array(feature_means)
    signs = np.where(feature_values - feature_means >= 0, 1, -1)
    impacts = importances * signs

    factors = [
        {"factor": name, "impact": float(impact)}
        for name, impact in zip(feature_names, impacts)
    ]
    factors.sort(key=lambda x: abs(x["impact"]), reverse=True)
    return factors[:top_n]
