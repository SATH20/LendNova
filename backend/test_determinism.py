"""
DETERMINISM TEST
Validates that same inputs always produce same outputs (Rule 5)
"""

from services.decision_orchestrator import run_full_assessment


def test_determinism():
    """Run same test case 10 times and verify identical outputs"""
    
    test_input = {
        'model_probability': 0.75,
        'declared_income': 6500,
        'verified_income': 6500,
        'declared_expense': 2800,
        'verified_expense': 2800,
        'verification_flags': [],
        'trust_score': 0.82,
        'fraud_probability': 0.12,
        'income_stability_score': 0.78,
        'expense_pattern_score': 0.75,
        'employment_type': 'Full-Time',
        'job_tenure': 4.0,
        'verification_status': 'VERIFIED',
    }
    
    print("=" * 80)
    print("DETERMINISM TEST - Running same input 10 times")
    print("=" * 80)
    
    results = []
    for i in range(10):
        result = run_full_assessment(test_input)
        results.append(result)
        print(f"\nRun {i+1}:")
        print(f"  Credit Score: {result['credit_score']}")
        print(f"  Risk Band: {result['risk_band']}")
        print(f"  Decision: {result['decision']}")
        print(f"  Approval Probability: {result['approval_probability']:.4f}")
    
    # Verify all results are identical
    first_result = results[0]
    all_identical = True
    
    for i, result in enumerate(results[1:], start=2):
        if (result['credit_score'] != first_result['credit_score'] or
            result['risk_band'] != first_result['risk_band'] or
            result['decision'] != first_result['decision'] or
            result['approval_probability'] != first_result['approval_probability']):
            print(f"\n[FAIL] DETERMINISM VIOLATION: Run {i} differs from Run 1")
            all_identical = False
    
    print("\n" + "=" * 80)
    if all_identical:
        print("[SUCCESS] DETERMINISM TEST PASSED - All outputs identical")
    else:
        print("[FAILURE] DETERMINISM TEST FAILED - Outputs vary")
    print("=" * 80)
    
    return all_identical


if __name__ == '__main__':
    test_determinism()
