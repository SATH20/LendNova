import os
import json
import joblib
import pandas as pd
from flask import Blueprint, request, jsonify, current_app
from marshmallow import ValidationError
from database.schemas import AssessmentInputSchema, AssessmentOutputSchema
from database.models import Assessment, db
from services.explainability import explain_decision
from utils.helpers import (
    credit_score_from_prob,
    risk_band_from_score,
    confidence_from_prob,
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
        credit_score = credit_score_from_prob(prob)
        risk_band = risk_band_from_score(credit_score)
        confidence_score = confidence_from_prob(prob)

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
            credit_score=credit_score,
            approval_probability=prob,
            fraud_probability=None,
            risk_band=risk_band,
            model_used=stats.get("model") or type(model).__name__,
            confidence_score=confidence_score,
            assessment_status="PRELIMINARY",
            assessment_stage="PRELIMINARY",
            verification_status="PENDING",
            trust_score=None,
            identity_status=None,
            verification_reasons=json.dumps([]),
            verification_flags=json.dumps([]),
            income_stability_score=None,
            expense_pattern_score=None,
        )

        db.session.add(assessment)
        db.session.commit()

        result = output_schema.dump(assessment)
        result["top_factors"] = top_factors
        result["fraud_probability"] = None
        result["fraud_flags"] = []
        result["assessment_status"] = "PRELIMINARY"
        result["verification_status"] = "PENDING"
        result["trust_score"] = None
        result["identity_status"] = None
        result["verification_reasons"] = []

        return jsonify(result), 200

    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
