"""
Standalone test script to demonstrate the identity verification system
(without database dependencies)
"""

import hashlib
from difflib import SequenceMatcher

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

def _name_consistency(name_claimed, name_ocr):
    score = _similarity(_normalize(name_claimed), _normalize(name_ocr))
    if name_claimed and name_ocr and score < 0.7:
        return score, "Name mismatch detected"
    return score, None

def _employer_consistency(employer_claimed, employer_ocr):
    if not employer_claimed or not employer_ocr:
        return 0.7, None
    score = _similarity(employer_claimed, employer_ocr)
    if score < 0.65:
        return score, "Employer mismatch detected"
    return score, None

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

def verify_identity_standalone(form_data, ocr_data):
    reasons = []
    
    # Name consistency
    name_score, name_reason = _name_consistency(form_data.get("name"), ocr_data.get("name"))
    if name_reason:
        reasons.append(name_reason)
    
    # Income consistency
    income_score, income_reason = _income_consistency(
        form_data.get("income"), ocr_data.get("income")
    )
    if income_reason:
        reasons.append(income_reason)
    
    # Employer consistency
    employer_score, employer_reason = _employer_consistency(
        form_data.get("employer"), ocr_data.get("employer")
    )
    if employer_reason:
        reasons.append(employer_reason)
    
    name_match_score = max(0.1, (0.5 * name_score + 0.3 * employer_score + 0.2 * income_score))
    
    # OCR confidence (simplified)
    fields = [ocr_data.get("name"), ocr_data.get("income"), ocr_data.get("employer")]
    present = sum(1 for field in fields if field not in (None, "", []))
    ocr_confidence = present / 3
    if ocr_confidence < 0.6:
        reasons.append("OCR confidence low")
    
    # Plausibility
    plausibility_score, plausibility_reasons = _plausibility_score(form_data)
    reasons.extend(plausibility_reasons)
    
    # Simplified scores (no PDF check, no behavioral check for standalone)
    authenticity_score = 1.0
    behavior_score = 0.8
    
    # Calculate trust score
    trust_score = (
        0.30 * name_match_score
        + 0.25 * plausibility_score
        + 0.20 * ocr_confidence
        + 0.15 * authenticity_score
        + 0.10 * behavior_score
    )
    trust_score = max(0.0, min(1.0, trust_score))
    fraud_probability = max(0.0, min(1.0, 1 - trust_score))
    
    # Determine status
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
    }

# Test Cases
print("=" * 70)
print("LENDNOVA IDENTITY VERIFICATION SYSTEM - TEST RESULTS")
print("=" * 70)
print()

# Test Case 1: Legitimate user with matching data
print("TEST CASE 1: Legitimate User (Matching Data)")
print("-" * 70)

form_data_1 = {
    "name": "John Smith",
    "income": 4500,
    "employer": "Tech Corp",
    "expenses": 1800,
    "employment_type": "Full-time",
    "job_tenure": 3.5
}

ocr_data_1 = {
    "name": "John Smith",
    "income": 4500,
    "employer": "Tech Corp"
}

result_1 = verify_identity_standalone(form_data_1, ocr_data_1)
print(f"✓ Trust Score: {result_1['trust_score']:.2%}")
print(f"✓ Fraud Probability: {result_1['fraud_probability']:.2%}")
print(f"✓ Identity Status: {result_1['identity_status']}")
print(f"✓ Issues Found: {len(result_1['verification_reasons'])}")
if result_1['verification_reasons']:
    for reason in result_1['verification_reasons']:
        print(f"  - {reason}")
print()

# Test Case 2: Mismatched income
print("TEST CASE 2: Income Mismatch")
print("-" * 70)

form_data_2 = {
    "name": "Jane Doe",
    "income": 5000,
    "employer": "Finance Inc",
    "expenses": 2000,
    "employment_type": "Full-time",
    "job_tenure": 2.0
}

ocr_data_2 = {
    "name": "Jane Doe",
    "income": 3500,  # Mismatch!
    "employer": "Finance Inc"
}

result_2 = verify_identity_standalone(form_data_2, ocr_data_2)
print(f"✓ Trust Score: {result_2['trust_score']:.2%}")
print(f"✓ Fraud Probability: {result_2['fraud_probability']:.2%}")
print(f"✓ Identity Status: {result_2['identity_status']}")
print(f"✓ Issues Found: {len(result_2['verification_reasons'])}")
if result_2['verification_reasons']:
    for reason in result_2['verification_reasons']:
        print(f"  - {reason}")
print()

# Test Case 3: Implausible data (student with high income)
print("TEST CASE 3: Implausible Data (Student with High Income)")
print("-" * 70)

form_data_3 = {
    "name": "Alex Student",
    "income": 8000,  # Too high for student
    "employer": "University",
    "expenses": 3000,
    "employment_type": "Student",
    "job_tenure": 0.5
}

ocr_data_3 = {
    "name": "Alex Student",
    "income": 8000,
    "employer": "University"
}

result_3 = verify_identity_standalone(form_data_3, ocr_data_3)
print(f"✓ Trust Score: {result_3['trust_score']:.2%}")
print(f"✓ Fraud Probability: {result_3['fraud_probability']:.2%}")
print(f"✓ Identity Status: {result_3['identity_status']}")
print(f"✓ Issues Found: {len(result_3['verification_reasons'])}")
if result_3['verification_reasons']:
    for reason in result_3['verification_reasons']:
        print(f"  - {reason}")
print()

# Test Case 4: Rounded income pattern
print("TEST CASE 4: Rounded Income Pattern")
print("-" * 70)

form_data_4 = {
    "name": "Bob Worker",
    "income": 50000,  # Suspiciously round
    "employer": "Big Company",
    "expenses": 20000,
    "employment_type": "Full-time",
    "job_tenure": 5.0
}

ocr_data_4 = {
    "name": "Bob Worker",
    "income": 50000,
    "employer": "Big Company"
}

result_4 = verify_identity_standalone(form_data_4, ocr_data_4)
print(f"✓ Trust Score: {result_4['trust_score']:.2%}")
print(f"✓ Fraud Probability: {result_4['fraud_probability']:.2%}")
print(f"✓ Identity Status: {result_4['identity_status']}")
print(f"✓ Issues Found: {len(result_4['verification_reasons'])}")
if result_4['verification_reasons']:
    for reason in result_4['verification_reasons']:
        print(f"  - {reason}")
print()

# Test Case 5: Name mismatch
print("TEST CASE 5: Name Mismatch")
print("-" * 70)

form_data_5 = {
    "name": "Michael Johnson",
    "income": 4200,
    "employer": "Retail Store",
    "expenses": 1700,
    "employment_type": "Full-time",
    "job_tenure": 2.5
}

ocr_data_5 = {
    "name": "Mike Jones",  # Different name!
    "income": 4200,
    "employer": "Retail Store"
}

result_5 = verify_identity_standalone(form_data_5, ocr_data_5)
print(f"✓ Trust Score: {result_5['trust_score']:.2%}")
print(f"✓ Fraud Probability: {result_5['fraud_probability']:.2%}")
print(f"✓ Identity Status: {result_5['identity_status']}")
print(f"✓ Issues Found: {len(result_5['verification_reasons'])}")
if result_5['verification_reasons']:
    for reason in result_5['verification_reasons']:
        print(f"  - {reason}")
print()

print("=" * 70)
print("VERIFICATION SYSTEM TEST COMPLETE")
print("=" * 70)
print()
print("Summary:")
print("- Test 1 (Legitimate): Should show VERIFIED status")
print("- Test 2 (Income Mismatch): Should show SUSPICIOUS/FAILED status")
print("- Test 3 (Implausible): Should flag student income issues")
print("- Test 4 (Rounded): Should detect rounded income pattern")
print("- Test 5 (Name Mismatch): Should flag name inconsistency")
