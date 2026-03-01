import json
from flask import Blueprint, request, jsonify
from services.identity_verification import verify_identity
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
                assessment.fraud_probability = result["fraud_probability"]
                assessment.trust_score = result["trust_score"]
                assessment.identity_status = result["identity_status"]
                assessment.verification_reasons = json.dumps(result["verification_reasons"])
                assessment.identity_hash = result["identity_hash"]
                assessment.assessment_status = "VERIFIED"
                assessment.verification_status = "COMPLETED"
                db.session.commit()

        return jsonify(result), 200

    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
