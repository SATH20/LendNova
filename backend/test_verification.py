"""
Test script to demonstrate the identity verification system
"""

from services.identity_verification import verify_identity

# Test Case 1: Legitimate user with matching data
print("=" * 60)
print("TEST CASE 1: Legitimate User (Matching Data)")
print("=" * 60)

form_data_1 = {
    "name": "John Smith",
    "income": 4500,
    "employer": "Tech Corp",
    "mobile": "+1234567890",
    "expenses": 1800,
    "employment_type": "Full-time",
    "job_tenure": 3.5
}

ocr_data_1 = {
    "name": "John Smith",
    "income": 4500,
    "employer": "Tech Corp"
}

result_1 = verify_identity(form_data_1, ocr_data_1, None)
print(f"Trust Score: {result_1['trust_score']:.2%}")
print(f"Fraud Probability: {result_1['fraud_probability']:.2%}")
print(f"Identity Status: {result_1['identity_status']}")
print(f"Verification Reasons: {result_1['verification_reasons']}")
print()

# Test Case 2: Mismatched income
print("=" * 60)
print("TEST CASE 2: Income Mismatch")
print("=" * 60)

form_data_2 = {
    "name": "Jane Doe",
    "income": 5000,
    "employer": "Finance Inc",
    "mobile": "+1987654321",
    "expenses": 2000,
    "employment_type": "Full-time",
    "job_tenure": 2.0
}

ocr_data_2 = {
    "name": "Jane Doe",
    "income": 3500,  # Mismatch!
    "employer": "Finance Inc"
}

result_2 = verify_identity(form_data_2, ocr_data_2, None)
print(f"Trust Score: {result_2['trust_score']:.2%}")
print(f"Fraud Probability: {result_2['fraud_probability']:.2%}")
print(f"Identity Status: {result_2['identity_status']}")
print(f"Verification Reasons: {result_2['verification_reasons']}")
print()

# Test Case 3: Implausible data (student with high income)
print("=" * 60)
print("TEST CASE 3: Implausible Data (Student with High Income)")
print("=" * 60)

form_data_3 = {
    "name": "Alex Student",
    "income": 8000,  # Too high for student
    "employer": "University",
    "mobile": "+1555555555",
    "expenses": 3000,
    "employment_type": "Student",
    "job_tenure": 0.5
}

ocr_data_3 = {
    "name": "Alex Student",
    "income": 8000,
    "employer": "University"
}

result_3 = verify_identity(form_data_3, ocr_data_3, None)
print(f"Trust Score: {result_3['trust_score']:.2%}")
print(f"Fraud Probability: {result_3['fraud_probability']:.2%}")
print(f"Identity Status: {result_3['identity_status']}")
print(f"Verification Reasons: {result_3['verification_reasons']}")
print()

# Test Case 4: Rounded income pattern
print("=" * 60)
print("TEST CASE 4: Rounded Income Pattern")
print("=" * 60)

form_data_4 = {
    "name": "Bob Worker",
    "income": 50000,  # Suspiciously round
    "employer": "Big Company",
    "mobile": "+1666666666",
    "expenses": 20000,
    "employment_type": "Full-time",
    "job_tenure": 5.0
}

ocr_data_4 = {
    "name": "Bob Worker",
    "income": 50000,
    "employer": "Big Company"
}

result_4 = verify_identity(form_data_4, ocr_data_4, None)
print(f"Trust Score: {result_4['trust_score']:.2%}")
print(f"Fraud Probability: {result_4['fraud_probability']:.2%}")
print(f"Identity Status: {result_4['identity_status']}")
print(f"Verification Reasons: {result_4['verification_reasons']}")
print()

# Test Case 5: Name mismatch
print("=" * 60)
print("TEST CASE 5: Name Mismatch")
print("=" * 60)

form_data_5 = {
    "name": "Michael Johnson",
    "income": 4200,
    "employer": "Retail Store",
    "mobile": "+1777777777",
    "expenses": 1700,
    "employment_type": "Full-time",
    "job_tenure": 2.5
}

ocr_data_5 = {
    "name": "Mike Jones",  # Different name!
    "income": 4200,
    "employer": "Retail Store"
}

result_5 = verify_identity(form_data_5, ocr_data_5, None)
print(f"Trust Score: {result_5['trust_score']:.2%}")
print(f"Fraud Probability: {result_5['fraud_probability']:.2%}")
print(f"Identity Status: {result_5['identity_status']}")
print(f"Verification Reasons: {result_5['verification_reasons']}")
print()

print("=" * 60)
print("VERIFICATION SYSTEM TEST COMPLETE")
print("=" * 60)
