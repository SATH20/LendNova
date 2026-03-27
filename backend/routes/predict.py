import os
import json
import joblib
import pandas as pd
from flask import Blueprint, request, jsonify, current_app
from marshmallow import ValidationError
from database.schemas import AssessmentInputSchema, AssessmentOutputSchema
from database.models import Assessment, db
from services.explainability import explain_decision
from services.decision_orchestrator import run_full_assessment
from utils.helpers import (
    mask_amount,
)

predict_bp = Blueprint('predict', __name__)
schema = AssessmentInputSchema()
output_schema = AssessmentOutputSchema()

@predict_bp.route('/predict', methods=['POST'])
def predict():
    try:
        data = schema.load(request.json)

        model_path = current_app.config["MODEL_PATH"]
        pipeline_path = current_app.config["PIPELINE_PATH"]
        stats_path = current_app.config["FEATURE_STATS_PATH"]

        if not os.path.exists(model_path) or not os.path.exists(pipeline_path):
            return jsonify({"error": "Model not trained yet."}), 503

        model = joblib.load(model_path)
        preprocessor = joblib.load(pipeline_path)
        stats = joblib.load(stats_path) if os.path.exists(stats_path) else {}

        df = pd.DataFrame([data])
        transformed = preprocessor.transform(df)
        if hasattr(transformed, "toarray"):
            transformed = transformed.toarray()

        prob = float(model.predict_proba(transformed)[0][1])

        feature_names = stats.get("feature_names")
        feature_means = stats.get("feature_means")
        if not feature_names:
            feature_names = preprocessor.named_steps["preprocess"].get_feature_names_out().tolist()

        top_factors = explain_decision(
            model,
            feature_names,
            transformed[0],
            feature_means,
            top_n=5,
        )

        # Run through decision orchestrator for final scoring
        orchestrator_input = {
            'model_probability': prob,
            'declared_income': mask_amount(data["income"]),
            'verified_income': None,
            'declared_expense': mask_amount(data["expenses"]),
            'verified_expense': None,
            'verification_flags': [],
            'trust_score': None,
            'fraud_probability': 0.0,
            'income_stability_score': None,
            'expense_pattern_score': None,
            'employment_type': data["employment_type"],
            'job_tenure': data["job_tenure"],
            'verification_status': 'PENDING',
        }
        
        decision_result = run_full_assessment(orchestrator_input)

        assessment = Assessment(
            income=mask_amount(data["income"]),
            expenses=mask_amount(data["expenses"]),
            employment_type=data["employment_type"],
            job_tenure=data["job_tenure"],
            declared_income=mask_amount(data["income"]),
            declared_expense=mask_amount(data["expenses"]),
            verified_income=None,
            verified_expense=None,
            verification_method=None,
            credit_score=decision_result['credit_score'],
            approval_probability=decision_result['approval_probability'],
            fraud_probability=0.0,
            risk_band=decision_result['risk_band'],
            decision=decision_result['decision'],
            model_used=stats.get("model") or type(model).__name__,
            confidence_score=decision_result['confidence_score'],
            assessment_status="PRELIMINARY",
            assessment_stage="PRELIMINARY",
            verification_status="PENDING",
            trust_score=None,
            identity_status=None,
            verification_reasons=json.dumps([]),
            verification_flags=json.dumps(decision_result.get('penalties_applied', [])),
            income_stability_score=None,
            expense_pattern_score=None,
        )

        db.session.add(assessment)
        db.session.commit()

        result = output_schema.dump(assessment)
        result["top_factors"] = top_factors
        result["fraud_probability"] = 0.0
        result["fraud_flags"] = []
        result["assessment_status"] = "PRELIMINARY"
        result["verification_status"] = "PENDING"
        result["trust_score"] = None
        result["identity_status"] = None
        result["verification_reasons"] = []
        result["decision"] = decision_result['decision']
        result["positive_factors"] = decision_result.get('positive_factors', [])
        result["risk_factors"] = decision_result.get('risk_factors', [])

        # Loan eligibility data
        loan_eligibility = decision_result.get('loan_eligibility', {})
        result["loan_eligibility"] = {
            'eligible_loan_amount': loan_eligibility.get('eligible_loan_amount', 0),
            'monthly_emi_estimate': loan_eligibility.get('monthly_emi_estimate', 0),
            'effective_income': loan_eligibility.get('effective_income', 0),
            'effective_expense': loan_eligibility.get('effective_expense', 0),
            'disposable_income': loan_eligibility.get('disposable_income', 0),
            'savings_ratio': loan_eligibility.get('savings_ratio', 0),
            'max_dti_ratio': loan_eligibility.get('max_dti_ratio', 0),
            'income_used': loan_eligibility.get('income_used', 'declared'),
            'expense_used': loan_eligibility.get('expense_used', 'declared'),
        }
        result["improvement_suggestions"] = loan_eligibility.get('improvement_suggestions', [])
        result["potential_increase"] = loan_eligibility.get('potential_increase', {})
        result["data_source"] = decision_result.get('data_source', {})

        return jsonify(result), 200

    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
