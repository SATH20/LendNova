"""
QA Validation Suite - Comprehensive Testing of Credit Decision Pipeline
Tests all system truth rules with realistic borrower scenarios
"""

from services.decision_orchestrator import run_full_assessment
import json


class TestResult:
    def __init__(self, test_name, passed, expected, actual, violations):
        self.test_name = test_name
        self.passed = passed
        self.expected = expected
        self.actual = actual
        self.violations = violations


def validate_truth_rules(test_name, input_data, result):
    """Validate all system truth rules"""
    violations = []
    
    # Rule 1: Higher risk must NEVER produce higher score
    if result['risk_band'] == 'High' and result['credit_score'] >= 750:
        violations.append("RULE 1 VIOLATED: High risk with score >= 750")
    if result['risk_band'] == 'Medium' and result['credit_score'] >= 850:
        violations.append("RULE 1 VIOLATED: Medium risk with score >= 850")
    
    # Rule 2: Verification flags MUST reduce score
    if input_data.get('verification_flags') and len(input_data['verification_flags']) > 0:
        if result['credit_score'] > 850:
            violations.append("RULE 2 VIOLATED: Verification flags present but score > 850")
    
    # Rule 3: Fraud probability > 0.4 can NEVER result in APPROVED
    if input_data.get('fraud_probability', 0) > 0.4 and result['decision'] == 'APPROVED':
        violations.append(f"RULE 3 VIOLATED: Fraud {input_data['fraud_probability']:.2f} but APPROVED")
    
    # Rule 4: Approval probability must correlate with score
    expected_approval = (result['credit_score'] - 300) / 600
    if abs(result['approval_probability'] - expected_approval) > 0.05:
        violations.append(f"RULE 4 VIOLATED: Approval {result['approval_probability']:.2f} doesn't match score-based {expected_approval:.2f}")
    
    # Rule 6: Perfect score (>850) allowed ONLY if fully verified
    if result['credit_score'] > 850:
        if input_data.get('verification_status') not in ['VERIFIED', 'COMPLETED']:
            violations.append(f"RULE 6 VIOLATED: Score {result['credit_score']} but status {input_data.get('verification_status')}")
        if input_data.get('verification_flags') and len(input_data['verification_flags']) > 0:
            violations.append(f"RULE 6 VIOLATED: Score {result['credit_score']} but has verification flags")
    
    # Rule 7: Income mismatch must downgrade risk
    if input_data.get('verified_income') is not None and input_data.get('declared_income', 0) > 0:
        income_diff_pct = abs(input_data['declared_income'] - input_data['verified_income']) / input_data['declared_income']
        if income_diff_pct > 0.12:
            if result['risk_band'] == 'Low':
                violations.append(f"RULE 7 VIOLATED: Income mismatch {income_diff_pct*100:.1f}% but still Low risk")
    
    # Rule 8: Partial verification cannot produce LOW risk + high approval
    if input_data.get('verification_status') == 'PARTIAL':
        if result['risk_band'] == 'Low' and result['approval_probability'] > 0.90:
            violations.append(f"RULE 8 VIOLATED: Partial verification but Low risk + {result['approval_probability']*100:.0f}% approval")
    
    # Rule 9: Decision must align with risk band
    if result['risk_band'] == 'Low' and result['decision'] not in ['APPROVED', 'REVIEW']:
        violations.append(f"RULE 9 VIOLATED: Low risk but decision is {result['decision']}")
    if result['risk_band'] == 'High' and result['decision'] != 'REJECTED':
        violations.append(f"RULE 9 VIOLATED: High risk but decision is {result['decision']}")
    
    return violations


def run_test_case(test_name, input_data, expected_behavior):
    """Run a single test case and validate"""
    print(f"\n{'='*80}")
    print(f"TEST CAS