import sys
sys.path.insert(0, '.')

print("Testing imports...")

try:
    import os
    print("✓ os")
except Exception as e:
    print("✗ os:", e)

try:
    import json
    print("✓ json")
except Exception as e:
    print("✗ json:", e)

try:
    import joblib
    print("✓ joblib")
except Exception as e:
    print("✗ joblib:", e)

try:
    import pandas as pd
    print("✓ pandas")
except Exception as e:
    print("✗ pandas:", e)

try:
    from flask import Blueprint, request, jsonify, current_app
    print("✓ flask")
except Exception as e:
    print("✗ flask:", e)

try:
    from werkzeug.utils import secure_filename
    print("✓ werkzeug")
except Exception as e:
    print("✗ werkzeug:", e)

try:
    from marshmallow import ValidationError
    print("✓ marshmallow")
except Exception as e:
    print("✗ marshmallow:", e)

try:
    from services.ocr_service import extract_text_from_image
    print("✓ services.ocr_service")
except Exception as e:
    print("✗ services.ocr_service:", e)

try:
    from services.identity_verification import verify_identity
    print("✓ services.identity_verification")
except Exception as e:
    print("✗ services.identity_verification:", e)

try:
    from services.verification_engine import verification_router
    print("✓ services.verification_engine")
except Exception as e:
    print("✗ services.verification_engine:", e)

try:
    from services.fraud_engine import detect_fraud
    print("✓ services.fraud_engine")
except Exception as e:
    print("✗ services.fraud_engine:", e)

try:
    from services.decision_orchestrator import run_full_assessment
    print("✓ services.decision_orchestrator")
except Exception as e:
    print("✗ services.decision_orchestrator:", e)

try:
    from explainability.shap_explainer import explain_with_shap
    print("✓ explainability.shap_explainer")
except Exception as e:
    print("✗ explainability.shap_explainer:", e)

try:
    from database.models import Assessment, Document, db
    print("✓ database.models")
except Exception as e:
    print("✗ database.models:", e)

try:
    from database.schemas import AssessmentInputSchema, AssessmentOutputSchema
    print("✓ database.schemas")
except Exception as e:
    print("✗ database.schemas:", e)

print("\nAll imports tested!")
