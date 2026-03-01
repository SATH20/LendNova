import os
import json
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from services.ocr_service import extract_text_from_image
from services.identity_verification import verify_identity
from services.verification_engine import verification_router, get_final_values
from database.models import Document, Assessment, db
from database.schemas import AssessmentInputSchema, AssessmentOutputSchema
from utils.helpers import mask_text

ocr_bp = Blueprint('ocr', __name__)
input_schema = AssessmentInputSchema()
output_schema = AssessmentOutputSchema()

def allowed_file(filename):
    allowed = current_app.config.get("ALLOWED_EXTENSIONS", {"png", "jpg", "jpeg", "pdf"})
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed

@ocr_bp.route('/ocr-extract', methods=['POST'])
def ocr_extract():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    filename = secure_filename(file.filename)
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)

    try:
        extracted_data = extract_text_from_image(file_path, current_app.config)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    if extracted_data is None:
        return jsonify({"error": "OCR failed"}), 500

    masked_text = mask_text(extracted_data.get("raw_text", ""))
    assessment_id = request.form.get("assessment_id")
    if assessment_id is not None:
        try:
            assessment_id = int(assessment_id)
        except ValueError:
            assessment_id = None

    document = Document(
        assessment_id=assessment_id,
        document_type=request.form.get("document_type", "unknown"),
        extracted_text=masked_text,
        fraud_flags="",
    )
    db.session.add(document)
    db.session.commit()

    assessment_payload = None
    verification_result = None
    underwriting_result = None

    has_income = extracted_data.get("income") is not None
    has_name = bool((extracted_data.get("name") or "").strip())
    has_structured = has_income or has_name
    
    document_type = request.form.get("document_type", "unknown")

    if assessment_id is not None:
        assessment = Assessment.query.get(assessment_id)
        if assessment:
            form_data = {
                "income": request.form.get("income"),
                "expenses": request.form.get("expenses"),
                "employment_type": request.form.get("employment_type"),
                "job_tenure": request.form.get("job_tenure"),
            }
            identity_data = {
                "name": request.form.get("name"),
                "employer": request.form.get("employer"),
                "mobile": request.form.get("mobile"),
            }
            try:
                if has_structured:
                    loaded_form = input_schema.load(form_data)
                    verification_form = {**loaded_form, **identity_data}
                    
                    # Run identity verification
                    verification_result = verify_identity(verification_form, extracted_data, file_path)
                    
                    # Run underwriting verification based on document type
                    ocr_payslip = None
                    ocr_bank = None
                    
                    if document_type == "payslip":
                        ocr_payslip = extracted_data
                    elif document_type == "bank_statement":
                        ocr_bank = extracted_data
                    else:
                        # Default: treat as payslip if has income
                        ocr_payslip = extracted_data if has_income else None
                    
                    # Run verification router
                    underwriting_result = verification_router(
                        assessment_data=verification_form,
                        ocr_data_payslip=ocr_payslip,
                        ocr_data_bank=ocr_bank,
                        file_path_payslip=file_path if document_type == "payslip" else None
                    )
                    
                    # Update assessment with verification results
                    assessment.fraud_probability = verification_result.get("fraud_probability")
                    assessment.trust_score = underwriting_result.get("trust_score", verification_result.get("trust_score"))
                    assessment.identity_status = verification_result.get("identity_status")
                    assessment.verification_reasons = json.dumps(
                        verification_result.get("verification_reasons", [])
                    )
                    assessment.verification_flags = json.dumps(
                        underwriting_result.get("verification_flags", [])
                    )
                    assessment.identity_hash = verification_result.get("identity_hash")
                    
                    # Update with underwriting data
                    assessment.verified_income = underwriting_result.get("verified_income")
                    assessment.verified_expense = underwriting_result.get("verified_expense")
                    assessment.verification_method = underwriting_result.get("verification_method")
                    assessment.income_stability_score = underwriting_result.get("income_stability_score")
                    assessment.expense_pattern_score = underwriting_result.get("expense_pattern_score")
                    assessment.assessment_stage = underwriting_result.get("assessment_stage", "PRELIMINARY")
                    assessment.verification_status = underwriting_result.get("verification_status", "PENDING")
                    
                    # Set assessment status based on verification
                    if underwriting_result.get("verification_status") == "VERIFIED":
                        assessment.assessment_status = "VERIFIED"
                    elif underwriting_result.get("verification_status") == "PARTIAL":
                        assessment.assessment_status = "PARTIAL"
                    else:
                        assessment.assessment_status = "PRELIMINARY"
                    
                    document.fraud_flags = json.dumps(
                        verification_result.get("verification_reasons", []) + 
                        underwriting_result.get("verification_flags", [])
                    )
                else:
                    assessment.fraud_probability = None
                    assessment.trust_score = None
                    assessment.identity_status = None
                    assessment.verification_reasons = json.dumps([])
                    assessment.verification_flags = json.dumps([])
                    assessment.assessment_status = "PRELIMINARY"
                    assessment.assessment_stage = "PRELIMINARY"
                    assessment.verification_status = "PENDING"
                    document.fraud_flags = ""
                db.session.commit()
                assessment_payload = output_schema.dump(assessment)
                if verification_result:
                    assessment_payload["fraud_flags"] = verification_result.get("verification_reasons", [])
                if underwriting_result:
                    assessment_payload["verification_flags"] = underwriting_result.get("verification_flags", [])
                    assessment_payload["verified_income"] = underwriting_result.get("verified_income")
                    assessment_payload["verified_expense"] = underwriting_result.get("verified_expense")
                    assessment_payload["verification_method"] = underwriting_result.get("verification_method")
                    assessment_payload["income_stability_score"] = underwriting_result.get("income_stability_score")
                    assessment_payload["expense_pattern_score"] = underwriting_result.get("expense_pattern_score")
            except Exception as e:
                print(f"Verification error: {str(e)}")
                db.session.rollback()

    response = {
        "name": extracted_data.get("name"),
        "income": extracted_data.get("income"),
        "employer": extracted_data.get("employer"),
        "extracted_text": masked_text,
        "document_id": document.id,
    }

    if assessment_payload:
        response["assessment"] = assessment_payload
    if verification_result:
        response["fraud_probability"] = verification_result.get("fraud_probability")
        response["fraud_flags"] = verification_result.get("verification_reasons", [])
        response["trust_score"] = verification_result.get("trust_score")
        response["identity_status"] = verification_result.get("identity_status")
        response["verification_reasons"] = verification_result.get("verification_reasons", [])
    if underwriting_result:
        response["verification_flags"] = underwriting_result.get("verification_flags", [])
        response["verified_income"] = underwriting_result.get("verified_income")
        response["verified_expense"] = underwriting_result.get("verified_expense")
        response["verification_method"] = underwriting_result.get("verification_method")
        response["verification_status"] = underwriting_result.get("verification_status")
        response["assessment_stage"] = underwriting_result.get("assessment_stage")
        response["income_stability_score"] = underwriting_result.get("income_stability_score")
        response["expense_pattern_score"] = underwriting_result.get("expense_pattern_score")

    return jsonify(response), 200
