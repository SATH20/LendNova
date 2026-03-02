import json
import os
import joblib
import pandas as pd
from flask import Blueprint, request, jsonify, current_app
from services.identity_verification import verify_identity
from services.decision_orchestrator import run_full_assessment
from services.explainability import explain_decision
from database.schemas import FraudCheckInputSchema
from database.models import Assessment, db
from marshmallow import ValidationError

fraud_bp = Blueprint('fraud', __name__)
schema = FraudCheckInputSchema()

@fraud_bp.route('/fraud-check', methods=['POST'])
def fraud_check():
    try:
        data = schema.load(request.json)
        
        ocr_data = data['ocr_data']
        form_data = data['form_data']
        
        has_income = ocr_data.get("income") is not None
        has_name = bool((ocr_data.get("name") or "").strip())
        has_structured = has_income or has_name
        if not has_structured:
            assessment_id = data.get("assessment_id")
            if assessment_id:
                assessment = Assessment.query.get(assessment_id)
                if assessment:
                    assessment.fraud_probability = None
                    assessment.trust_score = None
                    assessment.identity_status = None
                    assessment.verification_reasons = json.dumps([])
                    assessment.assessment_status = "PRELIMINARY"
                    assessment.verification_status = "PENDING"
                    db.session.commit()
            return jsonify(
                {
                    "fraud_probability": None,
                    "trust_score": None,
                    "identity_status": None,
                    "verification_reasons": [],
                }
            ), 200

        result = verify_identity(form_data, ocr_data, None)

        assessment_id = data.get("assessment_id")
        if assessment_id:
            assessment = Assessment.query.get(assessment_id)
            if assessment:
                # Load ML model to get original probability
                model_path = current_app.config["MODEL_PATH"]
                pipeline_path = current_app.config["PIPELINE_PATH"]
                stats_path = current_app.config["FEATURE_STATS_PATH"]
                
                model_probability = 0.5  # Default
                top_factors = []
                
                if os.path.exists(model_path) and os.path.exists(pipeline_path):
                    try:
                        model = joblib.load(model_path)
                        preprocessor = joblib.load(pipeline_path)
                        stats = joblib.load(stats_path) if os.path.exists(stats_path) else {}
                        
                        df = pd.DataFrame([form_data])
                        transformed = preprocessor.transform(df)
                        if hasattr(transformed, "toarray"):
                            transformed = transformed.toarray()
                        
                        model_probability = float(model.predict_proba(transformed)[0][1])
                        
                        # Get explainability
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
                    except Exception as e:
                        print(f"ML model error: {str(e)}")
                
                # Prepare orchestrator input
                orchestrator_input = {
                    'model_probability': model_probability,
                    'declared_income': form_data.get('income', 0),
                    'verified_income': None,
                    'declared_expense': form_data.get('expenses', 0),
                    'verified_expense': None,
                    'verification_flags': result.get('verification_reasons', []),
                    'trust_score': result.get('trust_score'),
                    'fraud_probability': result.get('fraud_probability', 0),
                    'income_stability_score': None,
                    'expense_pattern_score': None,
                    'employment_type': form_data.get('employment_type', ''),
                    'job_tenure': form_data.get('job_tenure', 0),
                    'verification_status': 'COMPLETED',
                }
                
                # Get final decision from orchestrator
                decision_result = run_full_assessment(orchestrator_input)
                
                # Update assessment with orchestrator results
                assessment.credit_score = decision_result['credit_score']
                assessment.approval_probability = decision_result['approval_probability']
                assessment.risk_band = decision_result['risk_band']
                assessment.decision = decision_result['decision']
                assessment.confidence_score = decision_result['confidence_score']
                assessment.fraud_probability = result["fraud_probability"]
                assessment.trust_score = result["trust_score"]
                assessment.identity_status = result["identity_status"]
                assessment.verification_reasons = json.dumps(result["verification_reasons"])
                assessment.identity_hash = result["identity_hash"]
                assessment.assessment_status = "VERIFIED"
                assessment.verification_status = "COMPLETED"
                db.session.commit()
                
                # Add decision to result
                result["decision"] = decision_result['decision']
                result["credit_score"] = decision_result['credit_score']
                result["risk_band"] = decision_result['risk_band']
                result["approval_probability"] = decision_result['approval_probability']
                result["top_factors"] = top_factors
                result["positive_factors"] = decision_result.get('positive_factors', [])
                result["risk_factors"] = decision_result.get('risk_factors', [])

        return jsonify(result), 200

    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
