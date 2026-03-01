from flask import Blueprint, request, jsonify
from services.fraud_engine import detect_fraud
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
        
        result = detect_fraud(form_data, ocr_data)

        assessment_id = data.get("assessment_id")
        if assessment_id:
            assessment = Assessment.query.get(assessment_id)
            if assessment:
                assessment.fraud_probability = result["fraud_probability"]
                assessment.assessment_status = "VERIFIED"
                assessment.verification_status = "COMPLETED"
                db.session.commit()

        return jsonify(result), 200

    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
