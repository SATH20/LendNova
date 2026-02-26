import pandas as pd
from sklearn.ensemble import IsolationForest
import numpy as np

def detect_fraud(form_data, ocr_data):
    """
    Checks for discrepancies between user input and document OCR.
    """
    flags = []
    
    # Rule 1: Income Check
    income_claimed = form_data.get('income', 0)
    income_ocr = ocr_data.get('income')
    
    if income_ocr is not None:
        diff = abs(income_claimed - income_ocr)
        if diff > 100: # Allow small margin
            flags.append("Significant Income Mismatch")
            
    # Rule 2: Employer Check (Mock)
    if ocr_data.get('employer') and "suspicious" in ocr_data.get('employer').lower():
        flags.append("High-Risk Employer Detected")
        
    # Anomaly Detection (Mock)
    # Normally use IsolationForest on metadata
    anomaly_score = 0.05
    if len(flags) > 0:
        anomaly_score += 0.3
        
    return {
        "fraud_probability": anomaly_score,
        "flags": flags
    }
