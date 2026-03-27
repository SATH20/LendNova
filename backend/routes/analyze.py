"""
Unified Pipeline Endpoint - POST /api/analyze
Executes complete credit assessment pipeline with all verification steps.

CORE PRINCIPLE: Verified (OCR) data overrides user-declared data.
Risk analysis is performed ONLY after OCR extraction and verification.
"""

import os
import json
import joblib
import pandas as pd
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from marshmallow import ValidationError

from services.ocr_service import extract_text_from_image
from services.identity_verification import verify_identity
from services.verification_engine import verification_router
from services.fraud_engine import detect_fraud
from services.decision_orchestrator import run_full_assessment
from explainability.shap_explainer import explain_with_shap

from database.models import Assessment, Document, db
from database.schemas import AssessmentInputSchema, AssessmentOutputSchema


analyze_bp = Blueprint('analyze', __name__)
input_schema = AssessmentInputSchema()
output_schema = AssessmentOutputSchema()


def allowed_file(filename):
    allowed = current_app.config.get("ALLOWED_EXTENSIONS", {"png", "jpg", "jpeg", "pdf"})
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


@analyze_bp.route('/analyze', methods=['POST'])
def analyze():
    try:
        form_data = {
            'income': float(request.form.get('income', 0)),
            'expenses': float(request.form.get('expenses', 0)),
            'employment_type': request.form.get('employment_type', ''),
            'job_tenure': float(request.form.get('job_tenure', 0)),
            'name': request.form.get('name', ''),
            'employer': request.form.get('employer', ''),
            'mobile': request.form.get('mobile', ''),
        }

        input_schema.load({
            'income': form_data['income'],
            'expenses': form_data['expenses'],
            'employment_type': form_data['employment_type'],
            'job_tenure': form_data['job_tenure'],
        })

        payslip_file = request.files.get('payslip')
        bank_statement_file = request.files.get('bank_statement')

        ocr_data_payslip = None
        ocr_data_bank = None
        payslip_path = None

        processing_summary = {
            'ocr_completed': False,
            'verification_completed': False,
            'fraud_checked': False,
            'data_source': {
                'income': 'declared',
                'expense': 'declared',
            },
        }

        # ── STEP 1: OCR EXTRACTION (Critical Stage) ──
        if payslip_file and allowed_file(payslip_file.filename):
            filename = secure_filename(payslip_file.filename)
            payslip_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            payslip_file.save(payslip_path)
            ocr_data_payslip = extract_text_from_image(payslip_path)
            processing_summary['ocr_completed'] = True

        if bank_statement_file and allowed_file(bank_statement_file.filename):
            filename = secure_filename(bank_statement_file.filename)
            bank_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            bank_statement_file.save(bank_path)
            ocr_data_bank = extract_text_from_image(bank_path)
            processing_summary['ocr_completed'] = True

        # ── STEP 2: VERIFICATION (Based on Employment Type) ──
        verification_result = verification_router(
            assessment_data=form_data,
            ocr_data_payslip=ocr_data_payslip,
            ocr_data_bank=ocr_data_bank,
            file_path_payslip=payslip_path
        )
        processing_summary['verification_completed'] = True

        # Track which data source is being used
        if verification_result.get('verified_income') is not None:
            processing_summary['data_source']['income'] = 'verified'
        if verification_result.get('verified_expense') is not None:
            processing_summary['data_source']['expense'] = 'verified'

        # ── STEP 3: FRAUD DETECTION ──
        fraud_result = detect_fraud(
            form_data=form_data,
            ocr_data=ocr_data_payslip or {}
        )
        processing_summary['fraud_checked'] = True

        # ── STEP 4: ML MODEL PREDICTION ──
        # Use verified data for ML prediction (verified overrides declared)
        model_path = current_app.config["MODEL_PATH"]
        pipeline_path = current_app.config["PIPELINE_PATH"]
        stats_path = current_app.config["FEATURE_STATS_PATH"]

        if not os.path.exists(model_path) or not os.path.exists(pipeline_path):
            return jsonify({"error": "Model not trained yet."}), 503

        model = joblib.load(model_path)
        preprocessor = joblib.load(pipeline_path)
        stats = joblib.load(stats_path) if os.path.exists(stats_path) else {}

        # CRITICAL: Use verified data for ML prediction when available
        ml_input = {
            'income': verification_result.get('verified_income') or form_data['income'],
            'expenses': verification_result.get('verified_expense') or form_data['expenses'],
            'employment_type': form_data['employment_type'],
            'job_tenure': form_data['job_tenure'],
        }

        df = pd.DataFrame([ml_input])
        transformed = preprocessor.transform(df)
        if hasattr(transformed, "toarray"):
            transformed = transformed.toarray()

        model_probability = float(model.predict_proba(transformed)[0][1])

        # ── STEP 5: DECISION ORCHESTRATION (Central Authority) ──
        # All data flows through the orchestrator for final decision
        orchestrator_input = {
            'model_probability': model_probability,
            'declared_income': form_data['income'],
            'verified_income': verification_result.get('verified_income'),
            'declared_expense': form_data['expenses'],
            'verified_expense': verification_result.get('verified_expense'),
            'verification_flags': verification_result.get('verification_flags', []),
            'trust_score': verification_result.get('trust_score'),
            'fraud_probability': fraud_result.get('fraud_probability', 0.0),
            'income_stability_score': verification_result.get('income_stability_score'),
            'expense_pattern_score': verification_result.get('expense_pattern_score'),
            'employment_type': form_data['employment_type'],
            'job_tenure': form_data['job_tenure'],
            'verification_status': verification_result.get('verification_status', 'PENDING'),
        }

        decision_result = run_full_assessment(orchestrator_input)

        # ── STEP 6: EXPLAINABILITY (SHAP Analysis) ──
        explainability_result = explain_with_shap(
            input_data=ml_input,
            model_path=model_path,
            pipeline_path=pipeline_path,
            stats_path=stats_path,
            top_n=3
        )

        # ── STEP 7: PERSIST TO DATABASE ──
        assessment = Assessment(
            income=form_data['income'],
            expenses=form_data['expenses'],
            employment_type=form_data['employment_type'],
            job_tenure=form_data['job_tenure'],
            declared_income=form_data['income'],
            declared_expense=form_data['expenses'],
            verified_income=verification_result.get('verified_income'),
            verified_expense=verification_result.get('verified_expense'),
            verification_method=verification_result.get('verification_method'),
            credit_score=decision_result['credit_score'],
            approval_probability=decision_result['approval_probability'],
            fraud_probability=fraud_result.get('fraud_probability', 0.0),
            risk_band=decision_result['risk_band'],
            decision=decision_result['decision'],
            model_used=stats.get("model") or type(model).__name__,
            confidence_score=decision_result['confidence_score'],
            assessment_status=verification_result.get('assessment_stage', 'PRELIMINARY'),
            assessment_stage=verification_result.get('assessment_stage', 'PRELIMINARY'),
            verification_status=verification_result.get('verification_status', 'PENDING'),
            trust_score=verification_result.get('trust_score'),
            identity_status=verification_result.get('verification_status'),
            verification_reasons=json.dumps(verification_result.get('verification_flags', [])),
            verification_flags=json.dumps(fraud_result.get('flags', [])),
            income_stability_score=verification_result.get('income_stability_score'),
            expense_pattern_score=verification_result.get('expense_pattern_score'),
        )

        db.session.add(assessment)
        db.session.commit()

        # ── STEP 8: BUILD RESPONSE WITH LOAN ELIGIBILITY ──
        loan_eligibility = decision_result.get('loan_eligibility', {})

        response = {
            'credit_score': decision_result['credit_score'],
            'risk_band': decision_result['risk_band'],
            'decision': decision_result['decision'],
            'approval_probability': decision_result['approval_probability'],
            'verification': {
                'status': verification_result.get('verification_status', 'PENDING'),
                'trust_score': verification_result.get('trust_score', 0.0),
                'flags': verification_result.get('verification_flags', []),
                'verified_income': verification_result.get('verified_income'),
                'verified_expense': verification_result.get('verified_expense'),
                'income_stability_score': verification_result.get('income_stability_score'),
                'expense_pattern_score': verification_result.get('expense_pattern_score'),
            },
            'fraud': {
                'fraud_probability': fraud_result.get('fraud_probability', 0.0),
                'flags': fraud_result.get('flags', []),
            },
            'explainability': {
                'positive_factors': explainability_result.get('positive_factors', []),
                'risk_factors': explainability_result.get('risk_factors', []),
            },
            'loan_eligibility': {
                'eligible_loan_amount': loan_eligibility.get('eligible_loan_amount', 0),
                'monthly_emi_estimate': loan_eligibility.get('monthly_emi_estimate', 0),
                'effective_income': loan_eligibility.get('effective_income', 0),
                'effective_expense': loan_eligibility.get('effective_expense', 0),
                'disposable_income': loan_eligibility.get('disposable_income', 0),
                'savings_ratio': loan_eligibility.get('savings_ratio', 0),
                'max_dti_ratio': loan_eligibility.get('max_dti_ratio', 0),
                'income_used': loan_eligibility.get('income_used', 'declared'),
                'expense_used': loan_eligibility.get('expense_used', 'declared'),
            },
            'improvement_suggestions': loan_eligibility.get('improvement_suggestions', []),
            'potential_increase': loan_eligibility.get('potential_increase', {}),
            'data_source': decision_result.get('data_source', {}),
            'processing_summary': processing_summary,
            'assessment_id': assessment.id,
            'timestamp': assessment.timestamp.isoformat() if assessment.timestamp else None,
        }

        return jsonify(response), 200

    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 400
    except Exception as e:
        current_app.logger.error(f"Analysis error: {str(e)}")
        return jsonify({"error": str(e)}), 500
