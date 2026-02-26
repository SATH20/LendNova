import pandas as pd
import numpy as np
import joblib
from flask import Blueprint, request, jsonify, current_app
from marshmallow import ValidationError
from database.schemas import AssessmentInputSchema, AssessmentOutputSchema
from database.models import Assessment, db
from services.explainability import explain_decision
import os

predict_bp = Blueprint('predict', __name__)
schema = AssessmentInputSchema()
output_schema = AssessmentOutputSchema()

@predict_bp.route('/predict', methods=['POST'])
def predict():
    try:
        # Validate Input
        data = schema.load(request.json)
        
        # Load Model Pipeline
        model_path = current_app.config['MODEL_PATH']
        if not os.path.exists(model_path):
            return jsonify({"error": "Model not trained yet."}), 503
            
        pipeline = joblib.load(model_path)
        
        # Prepare DataFrame
        df = pd.DataFrame([data])
        
        # Predict Probability
        prob = pipeline.predict_proba(df)[0][1] # Probability of Approval (Target=1)
        
        # Generate Credit Score (300-900 based on probability)
        # Higher prob -> Higher score
        base_score = 300
        score_range = 600
        credit_score = int(base_score + (prob * score_range))
        
        # Determine Risk Band
        if credit_score >= 750:
            risk_band = "Low"
        elif credit_score >= 650:
            risk_band = "Medium"
        else:
            risk_band = "High"
            
        # Feature Importance / Explainability
        # Access the classifier inside the pipeline
        model = pipeline.named_steps['model']
        # Transform features to get feature names if possible (mocking here for simplicity)
        # In a real scenario, use pipeline.named_steps['engineer'].get_feature_names_out()
        
        # We know our engineered features from feature_engineering.py
        feature_names = ['income', 'expenses', 'job_tenure', 'savings_ratio', 'expense_to_income_ratio', 'stability_score', 'employment_encoded']
        
        # Create a mock dataframe for explainability (needs coefficients/importances)
        # This part depends heavily on the model type.
        # Simplified for demo:
        top_factors = [
            {"factor": "Savings Ratio", "impact": 0.45},
            {"factor": "Job Tenure", "impact": 0.25},
            {"factor": "Expense Ratio", "impact": -0.15}
        ]
        
        # Save to Database
        assessment = Assessment(
            income=data['income'],
            expenses=data['expenses'],
            employment_type=data['employment_type'],
            job_tenure=data['job_tenure'],
            credit_score=credit_score,
            approval_probability=prob,
            fraud_probability=0.02, # Placeholder, updated by fraud check endpoint
            risk_band=risk_band,
            model_used=type(model).__name__,
            confidence_score=0.85 # Mock confidence
        )
        
        db.session.add(assessment)
        db.session.commit()
        
        result = output_schema.dump(assessment)
        result['top_factors'] = top_factors
        
        return jsonify(result), 200

    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
