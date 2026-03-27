"""
Decision Orchestrator - Central Authority for Credit Decisions
This module is the ONLY authority that produces final credit scores, risk bands, and decisions.
All verification, fraud, and ML results flow through here for deterministic scoring.

CORE PRINCIPLE: Verified data ALWAYS overrides user-declared data.
Risk analysis is performed on verified (OCR-extracted) financial data first.
"""

from utils.helpers import credit_score_from_prob
from services.loan_eligibility import calculate_loan_eligibility


class DecisionOrchestrator:
    """
    Centralized decision engine that ensures logical consistency across all credit decisions.
    Implements deterministic penalty-based scoring with strict business rules.
    Verified data always takes precedence over declared data.
    """

    # Penalty constants (deterministic) - CALIBRATED FOR REALISTIC LENDING
    PENALTY_INCOME_MISMATCH = 100
    PENALTY_EXPENSE_MISMATCH = 80
    PENALTY_LOW_TRUST = 70
    PENALTY_HIGH_FRAUD = 200
    PENALTY_MISSING_DOCS = 60
    PENALTY_EMPLOYMENT_INSTABILITY = 120
    PENALTY_INCOME_INSTABILITY = 50
    PENALTY_EXPENSE_PATTERN = 40

    # Thresholds
    INCOME_MISMATCH_THRESHOLD = 0.15
    EXPENSE_MISMATCH_THRESHOLD = 0.25
    TRUST_SCORE_THRESHOLD = 0.55
    FRAUD_PROBABILITY_THRESHOLD = 0.4
    FRAUD_REJECTION_THRESHOLD = 0.6
    INCOME_STABILITY_THRESHOLD = 0.5
    EXPENSE_PATTERN_THRESHOLD = 0.5

    # Risk bands - ADJUSTED FOR REALISTIC CREDIT SCORING
    RISK_LOW_THRESHOLD = 700
    RISK_MEDIUM_THRESHOLD = 550

    def __init__(self):
        pass

    def run_full_assessment(self, assessment_data):
        """
        Main orchestration method - produces final credit decision.

        IMPORTANT: This method uses verified data over declared data for all
        risk calculations. If verified data is available (from OCR), it takes
        precedence. Otherwise, declared data is used with penalties.

        Args:
            assessment_data (dict): Contains all inputs from ML, verification, fraud engines

        Returns:
            dict: Final decision with credit_score, risk_band, decision, approval_probability,
                  loan_eligibility, and improvement_suggestions
        """

        # Extract inputs
        model_probability = assessment_data.get('model_probability', 0.5)
        declared_income = assessment_data.get('declared_income', 0)
        verified_income = assessment_data.get('verified_income')
        declared_expense = assessment_data.get('declared_expense', 0)
        verified_expense = assessment_data.get('verified_expense')
        verification_flags = assessment_data.get('verification_flags', [])
        trust_score = assessment_data.get('trust_score')
        fraud_probability = assessment_data.get('fraud_probability', 0)
        income_stability_score = assessment_data.get('income_stability_score')
        expense_pattern_score = assessment_data.get('expense_pattern_score')
        employment_type = assessment_data.get('employment_type', '')
        job_tenure = assessment_data.get('job_tenure', 0)
        verification_status = assessment_data.get('verification_status', 'PENDING')

        # ── VERIFIED DATA OVERRIDE ──
        # Use verified data for all calculations when available
        effective_income = verified_income if verified_income is not None else declared_income
        effective_expense = verified_expense if verified_expense is not None else declared_expense

        # STEP 1: Calculate base score from ML probability
        base_score = credit_score_from_prob(model_probability)

        # STEP 2: Apply deterministic penalties
        penalties = []
        total_penalty = 0

        # Income mismatch penalty (verified vs declared)
        if verified_income is not None and declared_income > 0:
            income_diff_pct = abs(declared_income - verified_income) / declared_income
            if income_diff_pct > self.INCOME_MISMATCH_THRESHOLD:
                total_penalty += self.PENALTY_INCOME_MISMATCH
                penalties.append(f"Income mismatch: {income_diff_pct*100:.1f}% difference (declared: {declared_income:.0f}, verified: {verified_income:.0f})")

        # Expense mismatch penalty (verified vs declared)
        if verified_expense is not None and declared_expense > 0:
            expense_diff_pct = abs(declared_expense - verified_expense) / declared_expense
            if expense_diff_pct > self.EXPENSE_MISMATCH_THRESHOLD:
                total_penalty += self.PENALTY_EXPENSE_MISMATCH
                penalties.append(f"Expense mismatch: {expense_diff_pct*100:.1f}% difference (declared: {declared_expense:.0f}, verified: {verified_expense:.0f})")

        # Low trust score penalty
        if trust_score is not None and trust_score < self.TRUST_SCORE_THRESHOLD:
            total_penalty += self.PENALTY_LOW_TRUST
            penalties.append(f"Low trust score: {trust_score:.2f}")

        # High fraud probability penalty
        if fraud_probability > self.FRAUD_PROBABILITY_THRESHOLD:
            total_penalty += self.PENALTY_HIGH_FRAUD
            penalties.append(f"High fraud probability: {fraud_probability:.2f}")

        # Missing required documents penalty
        if verification_status in ['INCOMPLETE', 'PENDING']:
            emp_type_lower = employment_type.lower()
            if emp_type_lower in ['full-time', 'fulltime', 'self-employed', 'selfemployed', 'part-time', 'parttime']:
                total_penalty += self.PENALTY_MISSING_DOCS
                penalties.append("Required documents missing")

        # Employment instability penalty
        if employment_type.lower() in ['unemployed'] and declared_income > 2000:
            total_penalty += self.PENALTY_EMPLOYMENT_INSTABILITY
            penalties.append("Employment status inconsistent with income")

        # Income stability penalty
        if income_stability_score is not None and income_stability_score < self.INCOME_STABILITY_THRESHOLD:
            total_penalty += self.PENALTY_INCOME_INSTABILITY
            penalties.append(f"Low income stability: {income_stability_score:.2f}")

        # Expense pattern penalty
        if expense_pattern_score is not None and expense_pattern_score < self.EXPENSE_PATTERN_THRESHOLD:
            total_penalty += self.PENALTY_EXPENSE_PATTERN
            penalties.append(f"Irregular expense pattern: {expense_pattern_score:.2f}")

        # Additional penalties from verification flags
        if verification_flags:
            for flag in verification_flags:
                if 'mismatch' in flag.lower() and total_penalty < 500:
                    total_penalty += 30

        # ── EMPLOYMENT-TYPE DYNAMIC ADJUSTMENT ──
        # Apply different scoring adjustments based on employment type
        employment_adjustment = self._get_employment_adjustment(
            employment_type, job_tenure, effective_income, effective_expense
        )
        total_penalty += employment_adjustment.get('penalty', 0)
        if employment_adjustment.get('penalty_reason'):
            penalties.append(employment_adjustment['penalty_reason'])

        # Calculate final score
        final_score = base_score - total_penalty
        final_score = max(300, min(900, final_score))  # Clamp between 300-900

        # STEP 3: Determine risk band
        if final_score >= self.RISK_LOW_THRESHOLD:
            risk_band = "Low"
        elif final_score >= self.RISK_MEDIUM_THRESHOLD:
            risk_band = "Medium"
        else:
            risk_band = "High"

        # STEP 4: Determine final decision
        decision = self._determine_decision(
            final_score,
            risk_band,
            fraud_probability,
            trust_score,
            verification_status
        )

        # STEP 5: Calculate approval probability (aligned with score)
        approval_probability = (final_score - 300) / 600
        approval_probability = max(0.0, min(1.0, approval_probability))

        # STEP 6: Apply consistency rules
        approval_probability, risk_band, decision = self._enforce_consistency_rules(
            approval_probability,
            risk_band,
            decision,
            verification_flags,
            trust_score,
            fraud_probability,
            verification_status
        )

        # Build positive and risk factors
        positive_factors = self._extract_positive_factors(
            model_probability,
            job_tenure,
            employment_type,
            income_stability_score,
            expense_pattern_score,
            trust_score
        )

        risk_factors = penalties + verification_flags

        confidence_score = abs(approval_probability - 0.5) * 2

        # ── LOAN ELIGIBILITY CALCULATION ──
        loan_eligibility_input = {
            'credit_score': final_score,
            'declared_income': declared_income,
            'verified_income': verified_income,
            'declared_expense': declared_expense,
            'verified_expense': verified_expense,
            'employment_type': employment_type,
            'job_tenure': job_tenure,
            'trust_score': trust_score,
            'fraud_probability': fraud_probability,
            'income_stability_score': income_stability_score,
            'expense_pattern_score': expense_pattern_score,
            'verification_status': verification_status,
            'decision': decision,
        }
        loan_eligibility = calculate_loan_eligibility(loan_eligibility_input)

        return {
            'credit_score': final_score,
            'risk_band': risk_band,
            'decision': decision,
            'approval_probability': round(approval_probability, 4),
            'base_score': base_score,
            'total_penalty': total_penalty,
            'penalties_applied': penalties,
            'positive_factors': positive_factors,
            'risk_factors': risk_factors,
            'confidence_score': confidence_score,
            # Verified data usage info
            'effective_income': effective_income,
            'effective_expense': effective_expense,
            'data_source': {
                'income': 'verified' if verified_income is not None else 'declared',
                'expense': 'verified' if verified_expense is not None else 'declared',
            },
            # Loan eligibility
            'loan_eligibility': loan_eligibility,
        }

    def _get_employment_adjustment(self, employment_type, job_tenure, income, expense):
        """
        Dynamic adjustment based on employment type.
        Different employment types get different treatment.
        """
        emp_lower = employment_type.lower()
        result = {'penalty': 0, 'penalty_reason': None}

        savings_ratio = (income - expense) / max(income, 1) if income > 0 else 0

        if emp_lower in ['full-time', 'fulltime']:
            # Full-time: stable, but penalize very low savings
            if savings_ratio < 0.10 and income > 0:
                result['penalty'] = 30
                result['penalty_reason'] = f'Very low savings ratio ({savings_ratio*100:.1f}%) for salaried employee'

        elif emp_lower in ['self-employed', 'selfemployed']:
            # Self-employed: expect higher income variability but penalize low tenure
            if job_tenure < 2:
                result['penalty'] = 40
                result['penalty_reason'] = f'Short business tenure ({job_tenure:.1f} years) for self-employed'
            if savings_ratio < 0.15:
                result['penalty'] += 20
                if result['penalty_reason']:
                    result['penalty_reason'] += f'; Low savings ratio ({savings_ratio*100:.1f}%)'
                else:
                    result['penalty_reason'] = f'Low savings ratio ({savings_ratio*100:.1f}%) for self-employed'

        elif emp_lower in ['part-time', 'parttime']:
            # Part-time: moderate risk
            if income < 2000:
                result['penalty'] = 30
                result['penalty_reason'] = f'Low part-time income (₹{income:,.0f}/month)'

        elif emp_lower in ['student']:
            # Student: lenient but cap expectations
            if income > 8000:
                result['penalty'] = 20
                result['penalty_reason'] = 'Unusually high income for student status'

        elif emp_lower in ['unemployed']:
            # Unemployed: highest risk
            if expense > 0 and income < expense * 1.2:
                result['penalty'] = 50
                result['penalty_reason'] = 'Expenses nearly exceed income for unemployed applicant'

        return result

    def _determine_decision(self, score, risk_band, fraud_probability, trust_score, verification_status):
        """
        Determines final lending decision based on score and risk factors.
        """
        # Automatic rejection conditions (strict)
        if fraud_probability >= self.FRAUD_REJECTION_THRESHOLD:
            return "REJECTED"

        if trust_score is not None and trust_score < 0.3:
            return "REJECTED"

        # High risk handling
        if risk_band == "High":
            if fraud_probability > 0.5 or (trust_score is not None and trust_score < 0.35):
                return "REJECTED"
            if trust_score is not None and trust_score < 0.45:
                return "REJECTED"
            return "REVIEW"

        # Medium risk - always requires manual review
        if risk_band == "Medium":
            return "REVIEW"

        # Low risk - can be approved with conditions
        if verification_status in ['INCOMPLETE', 'PENDING']:
            return "REVIEW"

        if fraud_probability > 0.3:
            return "REVIEW"

        return "APPROVED"

    def _enforce_consistency_rules(self, approval_probability, risk_band, decision,
                                   verification_flags, trust_score, fraud_probability,
                                   verification_status):
        """
        Enforces strict consistency rules to prevent contradictory outputs.
        """
        # Rule 1: If verification flags exist, cap approval probability
        if verification_flags and len(verification_flags) > 0:
            approval_probability = min(approval_probability, 0.92)

        # Rule 2: Low trust reduces approval probability
        if trust_score is not None and trust_score < 0.5:
            if risk_band == "Low" and trust_score < 0.4:
                risk_band = "Medium"
            approval_probability = min(approval_probability, 0.80)

        # Rule 3: High fraud cannot be approved
        if fraud_probability > self.FRAUD_PROBABILITY_THRESHOLD:
            if decision == "APPROVED":
                decision = "REVIEW"
            approval_probability = min(approval_probability, 0.70)

        # Rule 4: Partial verification caps approval
        if verification_status == "PARTIAL":
            approval_probability = min(approval_probability, 0.85)

        # Rule 5: Pending verification caps approval
        if verification_status == "PENDING":
            approval_probability = min(approval_probability, 0.75)
            if decision == "APPROVED":
                decision = "REVIEW"

        # Rule 6: Incomplete verification for required docs
        if verification_status == "INCOMPLETE":
            approval_probability = min(approval_probability, 0.65)
            if decision == "APPROVED":
                decision = "REVIEW"

        # Rule 7: Decision must align with approval probability
        if decision == "APPROVED" and approval_probability < 0.60:
            decision = "REVIEW"

        if decision == "REJECTED" and approval_probability > 0.55:
            approval_probability = min(approval_probability, 0.55)

        # Rule 8: Review decisions should have moderate approval probability
        if decision == "REVIEW":
            if approval_probability > 0.90:
                approval_probability = min(approval_probability, 0.85)

        return approval_probability, risk_band, decision

    def _extract_positive_factors(self, model_probability, job_tenure, employment_type,
                                  income_stability, expense_pattern, trust_score):
        """
        Extracts positive factors that contributed to the decision.
        """
        factors = []

        if model_probability > 0.7:
            factors.append("Strong ML model prediction")

        if job_tenure > 3:
            factors.append(f"Stable employment: {job_tenure:.1f} years")

        if employment_type.lower() in ['full-time', 'fulltime']:
            factors.append("Full-time employment")

        if income_stability is not None and income_stability > 0.7:
            factors.append(f"High income stability: {income_stability:.2f}")

        if expense_pattern is not None and expense_pattern > 0.7:
            factors.append(f"Regular expense pattern: {expense_pattern:.2f}")

        if trust_score is not None and trust_score > 0.8:
            factors.append(f"High trust score: {trust_score:.2f}")

        return factors


# Singleton instance
_orchestrator = DecisionOrchestrator()


def run_full_assessment(assessment_data):
    """
    Public API for running full credit assessment.

    Args:
        assessment_data (dict): All inputs from ML, verification, fraud engines

    Returns:
        dict: Final decision with credit_score, risk_band, decision, approval_probability,
              loan_eligibility, and improvement_suggestions
    """
    return _orchestrator.run_full_assessment(assessment_data)
