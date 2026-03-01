import hashlib
from datetime import datetime, timedelta
from difflib import SequenceMatcher

from database.models import Assessment

try:
    from PyPDF2 import PdfReader
except Exception:
    PdfReader = None


def _normalize(value):
    if value is None:
        return ""
    return " ".join(str(value).lower().strip().split())


def _similarity(a, b):
    if not a or not b:
        return 0.6
    return SequenceMatcher(None, a, b).ratio()


def _income_consistency(income_claimed, income_ocr):
    if income_claimed is None or income_ocr is None:
        return 0.7, None
    diff_pct = abs(income_claimed - income_ocr) / max(income_claimed, 1)
    score = max(0.0, 1 - min(diff_pct / 0.3, 1))
    if diff_pct > 0.12:
        return score, "Income mismatch detected"
    return score, None


def _employer_consistency(employer_claimed, employer_ocr):
    if not employer_claimed or not employer_ocr:
        return 0.7, None
    score = _similarity(employer_claimed, employer_ocr)
    if score < 0.65:
        return score, "Employer mismatch detected"
    return score, None


def _name_consistency(name_claimed, name_ocr):
    score = _similarity(_normalize(name_claimed), _normalize(name_ocr))
    if name_claimed and name_ocr and score < 0.7:
        return score, "Name mismatch detected"
    return score, None


def _pdf_authenticity(file_path):
    if not file_path or not PdfReader or not file_path.lower().endswith(".pdf"):
        return 1.0, None
    try:
        reader = PdfReader(file_path)
        meta = reader.metadata or {}
        meta_text = " ".join([str(meta.get(key, "")) for key in meta.keys()]).lower()
        suspicious = ["canva", "photoshop", "online", "editor", "pdfforge", "smallpdf"]
        for token in suspicious:
            if token in meta_text:
                return 0.6, f"Suspicious document metadata: {token.title()}"
    except Exception:
        return 0.85, None
    return 1.0, None


def _ocr_confidence(extracted_data):
    fields = [
        extracted_data.get("name"),
        extracted_data.get("income"),
        extracted_data.get("employer"),
    ]
    present = sum(1 for field in fields if field not in (None, "", []))
    return present / 3, present


def _plausibility_score(form_data):
    reasons = []
    score = 1.0
    income = float(form_data.get("income", 0) or 0)
    expenses = float(form_data.get("expenses", 0) or 0)
    tenure = float(form_data.get("job_tenure", 0) or 0)
    employment = _normalize(form_data.get("employment_type"))

    if income > 20000 and tenure < 1:
        score -= 0.2
        reasons.append("High income with short tenure")
    if employment == "student" and income > 6000:
        score -= 0.25
        reasons.append("Student income unusually high")
    if employment == "unemployed" and income > 2000:
        score -= 0.3
        reasons.append("Unemployed income unusually high")
    if income > 0 and income % 1000 == 0:
        score -= 0.1
        reasons.append("Rounded income pattern detected")
    if income > 0 and expenses > income * 0.95:
        score -= 0.1
        reasons.append("Expense ratio unusually high")

    return max(0.1, score), reasons


def _behavior_score(identity_hash):
    if not identity_hash:
        return 0.7, ["Mobile not provided for behavioral checks"]
    now = datetime.utcnow()
    ten_minutes_ago = now - timedelta(minutes=10)
    day_ago = now - timedelta(hours=24)

    recent_count = Assessment.query.filter(
        Assessment.identity_hash == identity_hash,
        Assessment.timestamp >= ten_minutes_ago,
    ).count()
    daily_count = Assessment.query.filter(
        Assessment.identity_hash == identity_hash,
        Assessment.timestamp >= day_ago,
    ).count()

    score = 1.0
    reasons = []
    if recent_count > 1:
        score -= 0.25
        reasons.append("Rapid repeat submissions detected")
    if daily_count > 3:
        score -= 0.2
        reasons.append("Multiple applications in 24h window")

    return max(0.1, score), reasons


def verify_identity(form_data, ocr_data, file_path=None):
    reasons = []
    name_score, name_reason = _name_consistency(form_data.get("name"), ocr_data.get("name"))
    income_score, income_reason = _income_consistency(
        form_data.get("income"), ocr_data.get("income")
    )
    employer_score, employer_reason = _employer_consistency(
        form_data.get("employer"), ocr_data.get("employer")
    )

    if name_reason:
        reasons.append(name_reason)
    if income_reason:
        reasons.append(income_reason)
    if employer_reason:
        reasons.append(employer_reason)

    name_match_score = max(
        0.1, (0.5 * name_score + 0.3 * employer_score + 0.2 * income_score)
    )

    authenticity_score, authenticity_reason = _pdf_authenticity(file_path)
    if authenticity_reason:
        reasons.append(authenticity_reason)

    ocr_confidence, present_fields = _ocr_confidence(ocr_data)
    if ocr_confidence < 0.6:
        reasons.append("OCR confidence low")

    plausibility_score, plausibility_reasons = _plausibility_score(form_data)
    reasons.extend(plausibility_reasons)

    identity_input = f"{_normalize(form_data.get('name'))}|{_normalize(form_data.get('mobile'))}"
    identity_hash = hashlib.sha256(identity_input.encode("utf-8")).hexdigest() if identity_input else None
    behavior_score, behavior_reasons = _behavior_score(identity_hash)
    reasons.extend(behavior_reasons)

    trust_score = (
        0.30 * name_match_score
        + 0.25 * plausibility_score
        + 0.20 * ocr_confidence
        + 0.15 * authenticity_score
        + 0.10 * behavior_score
    )
    trust_score = max(0.0, min(1.0, trust_score))
    fraud_probability = max(0.0, min(1.0, 1 - trust_score))

    if trust_score >= 0.75:
        identity_status = "VERIFIED"
    elif trust_score >= 0.5:
        identity_status = "SUSPICIOUS"
    else:
        identity_status = "FAILED"

    return {
        "trust_score": round(trust_score, 4),
        "fraud_probability": round(fraud_probability, 4),
        "identity_status": identity_status,
        "verification_reasons": reasons,
        "name_match_score": round(name_match_score, 4),
        "ocr_confidence": round(ocr_confidence, 4),
        "authenticity_score": round(authenticity_score, 4),
        "plausibility_score": round(plausibility_score, 4),
        "behavior_score": round(behavior_score, 4),
        "identity_hash": identity_hash,
        "present_fields": present_fields,
    }
