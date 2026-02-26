from flask import Blueprint, request, jsonify, current_app
from services.fraud_engine import detect_fraud
from database.schemas import FraudCheckInputSchema
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
        
        return jsonify(result), 200

    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
