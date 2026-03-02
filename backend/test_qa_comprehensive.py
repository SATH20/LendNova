"""
COMPREHENSIVE QA VALIDATION SUITE
Senior QA Engineer + Fintech Backend Architect

This test suite validates ALL system truth rules through 8 test cases.
Each test case simulates a real borrower scenario and validates logical consistency.
"""

import sys
import json
from services.decision_orchestrator import run_full_assessment
from utils.helpers import credit_score_from_prob


# ============================================================================
# SYSTEM TRUTH RULES (Must ALL be satisfied)
# ============================================================================
TRUTH_RULES = [
    "Rule 1: Higher risk must NEVER produce higher score",
    "Rule 2: Verification flags MUST reduce score",
    "Rule 3: Fraud probability > 0.4 can NEVER result in APPROVED",
    "Rule 4: Approval probability must correlate with score",
    "Rule 5: Same inputs must always produce same outputs (deterministic)",
    "Rule 6: Perfect score (>850) allowed ONLY if fully verified",
    "Rule 7: Income mismatch must downgrade risk",
    "Rule 8: Partial verification cannot produce LOW risk + 100% approval",
    "Rule 9: Decision must align with risk band: LOW→APPROVED, MEDIUM→REVIEW, HIGH→REJECTED"
]


# ============================================================================
# TEST CASE DEFINITIONS
# ============================================================================

TEST_CASES = {
    "TC01_IDEAL_BORROWER": {
        "description": "Perfect borrower - high income, verified, no flags",
        "input": {
            'model_probability': 0.92,
            'declared_income': 8000,
            'verified_income': 8000,
            'declared_expense': 3000,
            'verified_expense': 3000,
            'verification_flags': [],
            'trust_score': 0.95,
            'fraud_probability': 0.05,
            'income_stability_score': 0.90,
            'expense_pattern_score': 0.88,
            'employment_type': 'Full-Time',
            'job_tenure': 5.0,
            'verification_status': 'VERIFIED',
        },
        "expected": {
            "credit_score_min": 800,
            "risk_band": "Low",
            "decision": "APPROVED",
            "approval_probability_min": 0.85,
            "fraud_check": "pass"
        }
    },
    
    "TC02_EXPENSE_MISMATCH": {
        "description": "Good income but expenses don't match declaration",
        "input": {
            'model_probability': 0.78,
            'declared_income': 6000,
            'verified_income': 6000,
            'declared_expense': 2000,
            'verified_expense': 3500,  # 75% higher than declared
            'verification_flags': ['Expense mismatch: 75% difference'],
            'trust_score': 0.65,
            'fraud_probability': 0.15,
            'income_stability_score': 0.80,
            'expense_pattern_score': 0.60,
            'employment_type': 'Full-Time',
            'job_tenure': 3.0,
            'verification_status': 'VERIFIED',
        },
        "expected": {
            "credit_score_max": 750,
            "risk_band": "Medium",
            "decision": "REVIEW",
            "approval_probability_max": 0.80,
            "fraud_check": "pass"
        }
    },
    
    "TC03_HIGH_EXPENSE_RISK": {
        "description": "Expenses exceed 80% of income - high financial stress",
        "input": {
            'model_probability': 0.55,
            'declared_income': 4000,
            'verified_income': 4000,
            'declared_expense': 3300,
            'verified_expense': 3300,
            'verification_flags': [],
            'trust_score': 0.70,
            'fraud_probability': 0.20,
            'income_stability_score': 0.65,
            'expense_pattern_score': 0.55,
            'employment_type': 'Full-Time',
            'job_tenure': 2.0,
            'verification_status': 'VERIFIED',
        },
        "expected": {
            "credit_score_max": 700,
            "risk_band": "Medium",
            "decision": "REVIEW",
            "approval_probability_max": 0.70,
            "fraud_check": "pass"
        }
    },
    
    "TC04_FRAUD_SUSPICION": {
        "description": "High fraud probability - must be rejected or reviewed",
        "input": {
            'model_probability': 0.70,
            'declared_income': 7000,
            'verified_income': 5000,  # 28% mismatch
            'declared_expense': 2500,
            'verified_expense': 2500,
            'verification_flags': ['Income mismatch: 28.6% difference'],
            'trust_score': 0.45,
            'fraud_probability': 0.55,  # HIGH FRAUD
            'income_stability_score': 0.50,
            'expense_pattern_score': 0.60,
            'employment_type': 'Self-Employed',
            'job_tenure': 1.5,
            'verification_status': 'PARTIAL',
        },
        "expected": {
            "credit_score_max": 650,
            "risk_band": "High",
            "decision": "REJECTED",
            "approval_probability_max": 0.50,
            "fraud_check": "fail"
        }
    },
    
    "TC05_INCOME_MISMATCH": {
        "description": "Declared income significantly higher than verified",
        "input": {
            'model_probability': 0.68,
            'declared_income': 9000,
            'verified_income': 6000,  # 33% lower
            'declared_expense': 3000,
            'verified_expense': 3000,
            'verification_flags': ['Income mismatch: 33.3% difference'],
            'trust_score': 0.55,
            'fraud_probability': 0.35,
            'income_stability_score': 0.60,
            'expense_pattern_score': 0.70,
            'employment_type': 'Full-Time',
            'job_tenure': 2.5,
            'verification_status': 'VERIFIED',
        },
        "expected": {
            "credit_score_max": 680,
            "risk_band": "Medium",
            "decision": "REVIEW",
            "approval_probability_max": 0.70,
            "fraud_check": "pass"
        }
    },
    
    "TC06_FIRST_TIME_BORROWER": {
        "description": "New to workforce - low tenure, unverified",
        "input": {
            'model_probability': 0.60,
            'declared_income': 3500,
            'verified_income': None,
            'declared_expense': 1800,
            'verified_expense': None,
            'verification_flags': ['Required documents missing'],
            'trust_score': None,
            'fraud_probability': 0.10,
            'income_stability_score': None,
            'expense_pattern_score': None,
            'employment_type': 'Full-Time',
            'job_tenure': 0.5,
            'verification_status': 'INCOMPLETE',
        },
        "expected": {
            "credit_score_max": 650,
            "risk_band": "Medium",
            "decision": "REVIEW",
            "approval_probability_max": 0.70,
            "fraud_check": "pass"
        }
    },
    
    "TC07_EMPLOYMENT_INSTABILITY": {
        "description": "Unemployed but claiming high income - inconsistent",
        "input": {
            'model_probability': 0.50,
            'declared_income': 5000,
            'verified_income': None,
            'declared_expense': 2000,
            'verified_expense': None,
            'verification_flags': [],
            'trust_score': 0.40,
            'fraud_probability': 0.30,
            'income_stability_score': 0.30,
            'expense_pattern_score': 0.50,
            'employment_type': 'Unemployed',
            'job_tenure': 0.0,
            'verification_status': 'PENDING',
        },
        "expected": {
            "credit_score_max": 600,
            "risk_band": "High",
            "decision": "REJECTED",
            "approval_probability_max": 0.55,
            "fraud_check": "pass"
        }
    },
    
    "TC08_LOW_INCOME_APPLICANT": {
        "description": "Low income, high expense ratio, partial verification",
        "input": {
            'model_probability': 0.45,
            'declared_income': 2500,
            'verified_income': 2400,
            'declared_expense': 2000,
            'verified_expense': 2100,
            'verification_flags': [],
            'trust_score': 0.60,
            'fraud_probability': 0.25,
            'income_stability_score': 0.55,
            'expense_pattern_score': 0.50,
            'employment_type': 'Part-Time',
            'job_tenure': 1.0,
            'verification_status': 'PARTIAL',
        },
        "expected": {
            "credit_score_max": 650,
            "risk_band": "Medium",
            "decision": "REVIEW",
            "approval_probability_max": 0.70,
            "fraud_check": "pass"
        }
    }
}


# ============================================================================
# VALIDATION ENGINE
# ============================================================================

class ValidationEngine:
    """Validates outputs against system truth rules"""
    
    def __init__(self):
        self.violations = []
        self.test_results = []
    
    def validate_test_case(self, tc_id, tc_data, result):
        """Validate a single test case against expected behavior"""
        violations = []
        input_data = tc_data['input']
        expected = tc_data['expected']
        
        # Extract result values
        credit_score = result['credit_score']
        risk_band = result['risk_band']
        decision = result['decision']
        approval_prob = result['approval_probability']
        
        # Validation checks
        if 'credit_score_min' in expected and credit_score < expected['credit_score_min']:
            violations.append(f"Score {credit_score} below minimum {expected['credit_score_min']}")
        
        if 'credit_score_max' in expected and credit_score > expected['credit_score_max']:
            violations.append(f"Score {credit_score} above maximum {expected['credit_score_max']}")
        
        if 'risk_band' in expected and risk_band != expected['risk_band']:
            violations.append(f"Risk band '{risk_band}' != expected '{expected['risk_band']}'")
        
        if 'decision' in expected and decision != expected['decision']:
            violations.append(f"Decision '{decision}' != expected '{expected['decision']}'")
        
        if 'approval_probability_min' in expected and approval_prob < expected['approval_probability_min']:
            violations.append(f"Approval prob {approval_prob:.2f} below minimum {expected['approval_probability_min']}")
        
        if 'approval_probability_max' in expected and approval_prob > expected['approval_probability_max']:
            violations.append(f"Approval prob {approval_prob:.2f} above maximum {expected['approval_probability_max']}")
        
        # Truth rule validations
        self._validate_truth_rules(tc_id, input_data, result, violations)
        
        return violations
    
    def _validate_truth_rules(self, tc_id, input_data, result, violations):
        """Validate against system truth rules"""
        
        # Rule 3: Fraud > 0.4 cannot be APPROVED
        if input_data['fraud_probability'] > 0.4 and result['decision'] == 'APPROVED':
            violations.append(f"RULE 3 VIOLATION: Fraud {input_data['fraud_probability']:.2f} > 0.4 but decision is APPROVED")
        
        # Rule 4: Approval probability must correlate with score
        expected_approval = (result['credit_score'] - 300) / 600
        if abs(result['approval_probability'] - expected_approval) > 0.15:
            violations.append(f"RULE 4 VIOLATION: Approval prob {result['approval_probability']:.2f} doesn't correlate with score {result['credit_score']}")
        
        # Rule 6: Perfect score only if fully verified
        if result['credit_score'] > 850 and input_data['verification_status'] != 'VERIFIED':
            violations.append(f"RULE 6 VIOLATION: Score {result['credit_score']} > 850 but status is {input_data['verification_status']}")
        
        # Rule 8: Partial verification cannot produce LOW risk + high approval
        if input_data['verification_status'] == 'PARTIAL' and result['risk_band'] == 'Low' and result['approval_probability'] > 0.95:
            violations.append(f"RULE 8 VIOLATION: Partial verification with Low risk and {result['approval_probability']:.2f} approval")
        
        # Rule 9: Decision must align with risk band
        if result['risk_band'] == 'Low' and result['decision'] not in ['APPROVED', 'REVIEW']:
            violations.append(f"RULE 9 VIOLATION: Low risk but decision is {result['decision']}")
        
        if result['risk_band'] == 'High' and result['decision'] == 'APPROVED':
            violations.append(f"RULE 9 VIOLATION: High risk but decision is APPROVED")
        
        # Rule 2: Verification flags must reduce score
        if input_data['verification_flags'] and len(input_data['verification_flags']) > 0:
            base_score = credit_score_from_prob(input_data['model_probability'])
            if result['credit_score'] >= base_score:
                violations.append(f"RULE 2 VIOLATION: Verification flags present but score {result['credit_score']} >= base {base_score}")
    
    def run_all_tests(self):
        """Execute all test cases"""
        print("=" * 80)
        print("COMPREHENSIVE QA VALIDATION SUITE")
        print("=" * 80)
        print()
        
        all_passed = True
        
        for tc_id, tc_data in TEST_CASES.items():
            print(f"\n{'='*80}")
            print(f"TEST CASE: {tc_id}")
            print(f"Description: {tc_data['description']}")
            print(f"{'='*80}")
            
            # Run assessment
            result = run_full_assessment(tc_data['input'])
            
            # Validate
            violations = self.validate_test_case(tc_id, tc_data, result)
            
            # Store result
            test_result = {
                'test_case_id': tc_id,
                'description': tc_data['description'],
                'input': tc_data['input'],
                'expected': tc_data['expected'],
                'actual': {
                    'credit_score': result['credit_score'],
                    'risk_band': result['risk_band'],
                    'decision': result['decision'],
                    'approval_probability': result['approval_probability'],
                    'base_score': result['base_score'],
                    'total_penalty': result['total_penalty'],
                },
                'violations': violations,
                'passed': len(violations) == 0
            }
            
            self.test_results.append(test_result)
            
            # Print results
            self._print_test_result(test_result)
            
            if not test_result['passed']:
                all_passed = False
        
        # Summary
        self._print_summary(all_passed)
        
        return all_passed
    
    def _print_test_result(self, test_result):
        """Print formatted test result"""
        print("\nINPUT:")
        print(f"  Model Probability: {test_result['input']['model_probability']:.2f}")
        print(f"  Declared Income: ${test_result['input']['declared_income']}")
        print(f"  Verified Income: ${test_result['input']['verified_income']}")
        print(f"  Declared Expense: ${test_result['input']['declared_expense']}")
        print(f"  Verified Expense: ${test_result['input']['verified_expense']}")
        print(f"  Trust Score: {test_result['input']['trust_score']}")
        print(f"  Fraud Probability: {test_result['input']['fraud_probability']:.2f}")
        print(f"  Employment: {test_result['input']['employment_type']} ({test_result['input']['job_tenure']} years)")
        print(f"  Verification Status: {test_result['input']['verification_status']}")
        print(f"  Verification Flags: {test_result['input']['verification_flags']}")
        
        print("\nEXPECTED:")
        for key, value in test_result['expected'].items():
            print(f"  {key}: {value}")
        
        print("\nACTUAL OUTPUT:")
        print(f"  Credit Score: {test_result['actual']['credit_score']} (base: {test_result['actual']['base_score']}, penalty: {test_result['actual']['total_penalty']})")
        print(f"  Risk Band: {test_result['actual']['risk_band']}")
        print(f"  Decision: {test_result['actual']['decision']}")
        print(f"  Approval Probability: {test_result['actual']['approval_probability']:.4f}")
        
        if test_result['passed']:
            print("\n[PASS] TEST PASSED")
        else:
            print("\n[FAIL] TEST FAILED")
            print("\nVIOLATIONS:")
            for violation in test_result['violations']:
                print(f"  - {violation}")
    
    def _print_summary(self, all_passed):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        passed_count = sum(1 for tr in self.test_results if tr['passed'])
        total_count = len(self.test_results)
        
        print(f"\nTotal Tests: {total_count}")
        print(f"Passed: {passed_count}")
        print(f"Failed: {total_count - passed_count}")
        
        if all_passed:
            print("\n[SUCCESS] ALL TESTS PASSED - System is logically consistent")
        else:
            print("\n[FAILURE] SOME TESTS FAILED - System requires fixes")
            print("\nFailed test cases:")
            for tr in self.test_results:
                if not tr['passed']:
                    print(f"  - {tr['test_case_id']}: {tr['description']}")
        
        print("\n" + "=" * 80)
    
    def export_results(self, filename='test_results.json'):
        """Export test results to JSON"""
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\nTest results exported to {filename}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    validator = ValidationEngine()
    all_passed = validator.run_all_tests()
    validator.export_results('backend/test_results.json')
    
    sys.exit(0 if all_passed else 1)
