"""
Test Decision Orchestrator - Verify deterministic scoring and logical consistency
"""

from services.decision_orchestrator import run_full_assessment


def test_preliminary_assessment():
    """Test 1: Preliminary assessment (no documents)"""
    print("\n=== TEST 1: Preliminary Assessment (No Documents) ===")
    
    data = {
        'model_probability': 0.85,
        'declared_income': 5000,
        'verified_income': None,
        'declared_expense': 2000,
        'verified_expense': None,
        'verification_flags': [],
        'trust_score': None,
        'fraud_probability': 0.0,
        'income_stability_score': None,
        'expense_pattern_score': None,
        'employment_type': 'Full-time',
        'job_tenure': 3.5,
        'verification_status': 'PENDING',
    }
    
    result = run_full_assessment(data)
    
    print(f"Credit Score: {result['credit_score']}")
    print(f"Risk Band: {result['risk_band']}")
    print(f"Decision: {result['decision']}")
    print(f"Approval Probability: {result['approval_probability']:.2%}")
    print(f"Penalties Applied: {result['penalties_applied']}")
    
    # Assertions
    assert result['decision'] in ['REVIEW', 'REJECTED'], "Pending verification should not be APPROVED"
    assert result['approval_probability'] <= 0.80, "Pending verification should cap approval"
    print("✓ Test 1 PASSED")


def test_verified_good_match():
    """Test 2: Verified assessment with good data match"""
    print("\n=== TEST 2: Verified Assessment (Good Match) ===")
    
    data = {
        'model_probability': 0.85,
        'declared_income': 5000,
        'verified_income': 5100,  # 2% difference - acceptable
        'declared_expense': 2000,
        'verified_expense': 2050,  # 2.5% difference - acceptable
        'verification_flags': [],
        'trust_score': 0.85,
        'fraud_probability': 0.05,
        'income_stability_score': 0.8,
        'expense_pattern_score': 0.75,
        'employment_type': 'Full-time',
        'job_tenure': 3.5,
        'verification_status': 'VERIFIED',
    }
    
    result = run_full_assessment(data)
    
    print(f"Credit Score: {result['credit_score']}")
    print(f"Risk Band: {result['risk_band']}")
    print(f"Decision: {result['decision']}")
    print(f"Approval Probability: {result['approval_probability']:.2%}")
    print(f"Penalties Applied: {result['penalties_applied']}")
    
    # Assertions
    assert result['credit_score'] >= 750, "Good match should yield high score"
    assert result['risk_band'] == 'Low', "Should be low risk"
    assert result['decision'] == 'APPROVED', "Should be approved"
    assert len(result['penalties_applied']) == 0, "No penalties should apply"
    print("✓ Test 2 PASSED")


def test_income_mismatch():
    """Test 3: Income mismatch detected"""
    print("\n=== TEST 3: Income Mismatch (>12%) ===")
    
    data = {
        'model_probability': 0.85,
        'declared_income': 5000,
        'verified_income': 4000,  # 20% difference - PENALTY
        'declared_expense': 2000,
        'verified_expense': 2000,
        'verification_flags': ['Income mismatch detected'],
        'trust_score': 0.65,
        'fraud_probability': 0.15,
        'income_stability_score': 0.6,
        'expense_pattern_score': 0.7,
        'employment_type': 'Full-time',
        'job_tenure': 3.5,
        'verification_status': 'PARTIAL',
    }
    
    result = run_full_assessment(data)
    
    print(f"Credit Score: {result['credit_score']}")
    print(f"Risk Band: {result['risk_band']}")
    print(f"Decision: {result['decision']}")
    print(f"Approval Probability: {result['approval_probability']:.2%}")
    print(f"Penalties Applied: {result['penalties_applied']}")
    
    # Assertions
    assert result['credit_score'] < 750, "Mismatch should reduce score"
    assert 'Income mismatch' in str(result['penalties_applied']), "Income penalty should apply"
    assert result['decision'] != 'APPROVED', "Should not be approved with mismatch"
    print("✓ Test 3 PASSED")


def test_high_fraud_probability():
    """Test 4: High fraud probability"""
    print("\n=== TEST 4: High Fraud Probability ===")
    
    data = {
        'model_probability': 0.85,
        'declared_income': 5000,
        'verified_income': 5000,
        'declared_expense': 2000,
        'verified_expense': 2000,
        'verification_flags': ['Suspicious document metadata'],
        'trust_score': 0.45,  # Low trust
        'fraud_probability': 0.65,  # HIGH FRAUD
        'income_stability_score': 0.7,
        'expense_pattern_score': 0.7,
        'employment_type': 'Full-time',
        'job_tenure': 3.5,
        'verification_status': 'VERIFIED',
    }
    
    result = run_full_assessment(data)
    
    print(f"Credit Score: {result['credit_score']}")
    print(f"Risk Band: {result['risk_band']}")
    print(f"Decision: {result['decision']}")
    print(f"Approval Probability: {result['approval_probability']:.2%}")
    print(f"Penalties Applied: {result['penalties_applied']}")
    
    # Assertions
    assert result['decision'] == 'REJECTED', "High fraud should be rejected"
    assert result['credit_score'] < 650, "High fraud should yield low score"
    assert 'fraud' in str(result['penalties_applied']).lower(), "Fraud penalty should apply"
    print("✓ Test 4 PASSED")


def test_consistency_rules():
    """Test 5: Consistency rules enforcement"""
    print("\n=== TEST 5: Consistency Rules ===")
    
    # Scenario: High ML probability but low trust - should NOT be low risk
    data = {
        'model_probability': 0.95,  # Very high
        'declared_income': 5000,
        'verified_income': 5000,
        'declared_expense': 2000,
        'verified_expense': 2000,
        'verification_flags': ['Multiple applications detected'],
        'trust_score': 0.45,  # LOW TRUST
        'fraud_probability': 0.35,
        'income_stability_score': 0.7,
        'expense_pattern_score': 0.7,
        'employment_type': 'Full-time',
        'job_tenure': 3.5,
        'verification_status': 'VERIFIED',
    }
    
    result = run_full_assessment(data)
    
    print(f"Credit Score: {result['credit_score']}")
    print(f"Risk Band: {result['risk_band']}")
    print(f"Decision: {result['decision']}")
    print(f"Approval Probability: {result['approval_probability']:.2%}")
    print(f"Penalties Applied: {result['penalties_applied']}")
    
    # Assertions
    assert result['risk_band'] != 'Low', "Low trust cannot be low risk"
    assert result['approval_probability'] <= 0.75, "Low trust should cap approval"
    assert result['decision'] != 'APPROVED', "Should not approve with low trust"
    print("✓ Test 5 PASSED")


def test_determinism():
    """Test 6: Same input produces same output (determinism)"""
    print("\n=== TEST 6: Determinism Test ===")
    
    data = {
        'model_probability': 0.75,
        'declared_income': 4500,
        'verified_income': 4600,
        'declared_expense': 1800,
        'verified_expense': 1850,
        'verification_flags': [],
        'trust_score': 0.78,
        'fraud_probability': 0.08,
        'income_stability_score': 0.72,
        'expense_pattern_score': 0.68,
        'employment_type': 'Full-time',
        'job_tenure': 2.5,
        'verification_status': 'VERIFIED',
    }
    
    result1 = run_full_assessment(data)
    result2 = run_full_assessment(data)
    result3 = run_full_assessment(data)
    
    print(f"Run 1: Score={result1['credit_score']}, Decision={result1['decision']}")
    print(f"Run 2: Score={result2['credit_score']}, Decision={result2['decision']}")
    print(f"Run 3: Score={result3['credit_score']}, Decision={result3['decision']}")
    
    # Assertions
    assert result1['credit_score'] == result2['credit_score'] == result3['credit_score'], "Scores must be identical"
    assert result1['decision'] == result2['decision'] == result3['decision'], "Decisions must be identical"
    assert result1['approval_probability'] == result2['approval_probability'] == result3['approval_probability'], "Probabilities must be identical"
    print("✓ Test 6 PASSED - System is deterministic")


def test_missing_documents_penalty():
    """Test 7: Missing required documents for full-time"""
    print("\n=== TEST 7: Missing Required Documents ===")
    
    data = {
        'model_probability': 0.80,
        'declared_income': 5000,
        'verified_income': None,
        'declared_expense': 2000,
        'verified_expense': None,
        'verification_flags': [],
        'trust_score': None,
        'fraud_probability': 0.0,
        'income_stability_score': None,
        'expense_pattern_score': None,
        'employment_type': 'Full-time',  # Requires documents
        'job_tenure': 3.0,
        'verification_status': 'INCOMPLETE',
    }
    
    result = run_full_assessment(data)
    
    print(f"Credit Score: {result['credit_score']}")
    print(f"Risk Band: {result['risk_band']}")
    print(f"Decision: {result['decision']}")
    print(f"Approval Probability: {result['approval_probability']:.2%}")
    print(f"Penalties Applied: {result['penalties_applied']}")
    
    # Assertions
    assert 'documents missing' in str(result['penalties_applied']).lower(), "Missing docs penalty should apply"
    assert result['decision'] != 'APPROVED', "Cannot approve without required docs"
    print("✓ Test 7 PASSED")


if __name__ == '__main__':
    print("=" * 70)
    print("DECISION ORCHESTRATOR TEST SUITE")
    print("=" * 70)
    
    try:
        test_preliminary_assessment()
        test_verified_good_match()
        test_income_mismatch()
        test_high_fraud_probability()
        test_consistency_rules()
        test_determinism()
        test_missing_documents_penalty()
        
        print("\n" + "=" * 70)
        print("✓✓✓ ALL TESTS PASSED ✓✓✓")
        print("=" * 70)
        print("\nThe Decision Orchestrator is working correctly!")
        print("System is deterministic, logically consistent, and production-ready.")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        raise
