"""
Decision Orchestrator - Central Authority for Credit Decisions
This module is the ONLY authority that produces final credit scores, risk bands, and decisions.
All verification, fraud, and ML results flow through here for deterministic scoring.
"""

from utils.helpers import credit_score_from_prob


class DecisionOrchestrator:
    """
    Centralized decision engine that ensures logical consistency across all credit decisions.
    Implements deterministic penalty-based scoring with strict business rules.
    """
    
    # Penalty constants (deterministic)
    PENALTY_INCOME_MISMATCH = 200
    PENALTY_EXPENSE_MISMATCH = 150
    PENALTY_LOW_TRUST = 120
    PENALTY_HIGH_FRAUD = 250
    PENALTY_MISSING_DOCS = 100
    PENALTY_EMPLOYMENT_INSTABILITY = 80
    PENALTY_INCOME_INSTABILITY = 70
    PENALTY_EXPENSE_PATTERN = 50
    
    # Thresholds
    INCOME_MISMATCH_THRESHOLD = 0.12
    EXPENSE_MISMATCH_THRESHOLD = 0.20
    TRUST_SCORE_THRESHOLD = 0.6
    FRAUD_PROBABILITY_THRESHOLD = 0.4
    FRAUD_REJECTION_THRESHOLD = 0.6
    INCOME_STABILITY_THRESHOLD = 0.5
    EXPENSE_PATTERN_THRESHOLD = 0.5
    
    # Risk bands
    RISK_LOW_THRESHOLD = 750
    RISK_MEDIUM_THRESHOLD = 650
    
    def __init__(self):
        pass
    
    def run_full_assessment(self, assessment_data):
        """
        Main orchestration method - produces final credit decision.
        
        Args:
            assessment_data (dict): Contains all inputs from ML, verification, fraud engines
            
        Returns:
            dict: Final decision with credit_score, risk_band, decision, approval_probability
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
        
        # STEP 1: Calculate base score from ML probability
        base_score = credit_score_from_prob(model_probability)
        
        # STEP 2: Apply deterministic penalties
        penalties = []
        total_penalty = 0
        
        # Income mismatch penalty
        if verified_income is not None and declared_income > 0:
            income_diff_pct = abs(declared_income - verified_income) / declared_income
            if income_diff_pct > self.INCOME_MISMATCH_THRESHOLD:
                total_penalty += self.PENALTY_INCOME_MISMATCH
                penalties.append(f"Income mismatch: {income_diff_pct*100:.1f}% difference")
        
        # Expense mismatch penalty
        if verified_expense is not None and declared_expense > 0:
            expense_diff_pct = abs(declared_expense - verified_expense) / declared_expense
            if expense_diff_pct > self.EXPENSE_MISMATCH_THRESHOLD:
                total_penalty += self.PENALTY_EXPENSE_MISMATCH
                penalties.append(f"Expense mismatch: {expense_diff_pct*100:.1f}% difference")
        
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
            'confidence_score': abs(approval_probability - 0.5) * 2,  # Confidence metric
        }
    
    def _determine_decision(self, score, risk_band, fraud_probability, trust_score, verification_status):
        """
        Determines final lending decision based on score and risk factors.
        """
        # Automatic rejection conditions
        if fraud_probability >= self.FRAUD_REJECTION_THRESHOLD:
            return "REJECTED"
        
        if trust_score is not None and trust_score < 0.3:
            return "REJECTED"
        
        if risk_band == "High":
            return "REJECTED"
        
        if risk_band == "Medium":
            # Medium risk requires manual review
            if fraud_probability > 0.3 or (trust_score is not None and trust_score < 0.5):
                return "REVIEW"
            return "REVIEW"
        
        # Low risk
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
            approval_probability = min(approval_probability, 0.94)
        
        # Rule 2: Low trust cannot be low risk
        if trust_score is not None and trust_score < 0.5:
            if risk_band == "Low":
                risk_band = "Medium"
            approval_probability = min(approval_probability, 0.75)
        
        # Rule 3: High fraud cannot be approved
        if fraud_probability > self.FRAUD_PROBABILITY_THRESHOLD:
            if decision == "APPROVED":
                decision = "REVIEW"
            approval_probability = min(approval_probability, 0.65)
        
        # Rule 4: Partial verification cannot yield perfect score
        if verification_status == "PARTIAL":
            approval_probability = min(approval_probability, 0.88)
        
        # Rule 5: Pending verification cannot be approved
        if verification_status == "PENDING":
            approval_probability = min(approval_probability, 0.80)
            if decision == "APPROVED":
                decision = "REVIEW"
        
        # Rule 6: Incomplete verification for required docs
        if verification_status == "INCOMPLETE":
            approval_probability = min(approval_probability, 0.70)
            if decision == "APPROVED":
                decision = "REVIEW"
        
        # Rule 7: Decision must align with approval probability
        if decision == "APPROVED" and approval_probability < 0.65:
            decision = "REVIEW"
        
        if decision == "REJECTED" and approval_probability > 0.50:
            approval_probability = min(approval_probability, 0.50)
        
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
        dict: Final decision with credit_score, risk_band, decision, approval_probability
    """
    return _orchestrator.run_full_assessment(assessment_data)
