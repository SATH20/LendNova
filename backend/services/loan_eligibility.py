"""
Loan Eligibility Calculator
Calculates maximum loan amount based on verified financial data,
employment type, and behavioral metrics. Provides actionable improvement suggestions.
"""


# Employment-type specific multipliers for loan calculation
EMPLOYMENT_MULTIPLIERS = {
    'full-time': {'income_factor': 15, 'max_dti': 0.50, 'tenure_bonus': 1.0},
    'fulltime': {'income_factor': 15, 'max_dti': 0.50, 'tenure_bonus': 1.0},
    'self-employed': {'income_factor': 10, 'max_dti': 0.40, 'tenure_bonus': 0.8},
    'selfemployed': {'income_factor': 10, 'max_dti': 0.40, 'tenure_bonus': 0.8},
    'part-time': {'income_factor': 8, 'max_dti': 0.35, 'tenure_bonus': 0.7},
    'parttime': {'income_factor': 8, 'max_dti': 0.35, 'tenure_bonus': 0.7},
    'student': {'income_factor': 5, 'max_dti': 0.25, 'tenure_bonus': 0.5},
    'unemployed': {'income_factor': 2, 'max_dti': 0.15, 'tenure_bonus': 0.3},
}

DEFAULT_MULTIPLIER = {'income_factor': 8, 'max_dti': 0.35, 'tenure_bonus': 0.7}

# Score-based adjustment tiers
SCORE_TIERS = [
    (800, 1.20),   # Excellent
    (750, 1.10),   # Very Good
    (700, 1.00),   # Good
    (650, 0.85),   # Fair
    (600, 0.65),   # Below Average
    (550, 0.45),   # Poor
    (0,   0.25),   # Very Poor
]


def calculate_loan_eligibility(assessment_data):
    """
    Calculate loan eligibility amount based on verified financial data.

    Args:
        assessment_data (dict): Contains:
            - credit_score: int (300-900)
            - verified_income: float or None
            - declared_income: float
            - verified_expense: float or None
            - declared_expense: float
            - employment_type: str
            - job_tenure: float (years)
            - trust_score: float or None (0-1)
            - fraud_probability: float (0-1)
            - income_stability_score: float or None (0-1)
            - expense_pattern_score: float or None (0-1)
            - verification_status: str
            - decision: str (APPROVED, REVIEW, REJECTED)

    Returns:
        dict: Loan eligibility details with improvement suggestions
    """

    credit_score = assessment_data.get('credit_score', 300)
    declared_income = float(assessment_data.get('declared_income', 0))
    verified_income = assessment_data.get('verified_income')
    declared_expense = float(assessment_data.get('declared_expense', 0))
    verified_expense = assessment_data.get('verified_expense')
    employment_type = (assessment_data.get('employment_type', '') or '').lower()
    job_tenure = float(assessment_data.get('job_tenure', 0))
    trust_score = assessment_data.get('trust_score')
    fraud_probability = float(assessment_data.get('fraud_probability', 0))
    income_stability = assessment_data.get('income_stability_score')
    expense_pattern = assessment_data.get('expense_pattern_score')
    verification_status = assessment_data.get('verification_status', 'PENDING')
    decision = assessment_data.get('decision', 'REVIEW')

    # STEP 1: Use verified data over declared data (core requirement)
    effective_income = verified_income if verified_income is not None else declared_income
    effective_expense = verified_expense if verified_expense is not None else declared_expense

    # STEP 2: Calculate disposable income (monthly surplus)
    disposable_income = max(0, effective_income - effective_expense)
    savings_ratio = disposable_income / max(effective_income, 1)

    # STEP 3: Get employment-specific multipliers
    emp_config = EMPLOYMENT_MULTIPLIERS.get(employment_type, DEFAULT_MULTIPLIER)
    income_factor = emp_config['income_factor']
    max_dti = emp_config['max_dti']
    tenure_bonus = emp_config['tenure_bonus']

    # STEP 4: Calculate base eligible amount using DTI (debt-to-income) method
    # Maximum monthly EMI the borrower can afford
    max_monthly_emi = disposable_income * max_dti
    # Assume 12-month loan tenure for base calculation
    base_loan_amount = max_monthly_emi * 12

    # STEP 5: Apply income factor method (alternative calculation)
    income_based_amount = effective_income * income_factor

    # STEP 6: Take the more conservative estimate
    raw_eligible_amount = min(base_loan_amount, income_based_amount)

    # STEP 7: Apply credit score multiplier
    score_multiplier = 0.25
    for threshold, multiplier in SCORE_TIERS:
        if credit_score >= threshold:
            score_multiplier = multiplier
            break

    # STEP 8: Apply tenure bonus
    tenure_multiplier = 1.0
    if job_tenure >= 5:
        tenure_multiplier = 1.0 + (tenure_bonus * 0.15)
    elif job_tenure >= 3:
        tenure_multiplier = 1.0 + (tenure_bonus * 0.10)
    elif job_tenure >= 1:
        tenure_multiplier = 1.0 + (tenure_bonus * 0.05)
    else:
        tenure_multiplier = 0.90  # Slight reduction for very short tenure

    # STEP 9: Apply stability bonuses/penalties
    stability_multiplier = 1.0
    if income_stability is not None:
        if income_stability >= 0.8:
            stability_multiplier += 0.05
        elif income_stability < 0.5:
            stability_multiplier -= 0.10

    if expense_pattern is not None:
        if expense_pattern >= 0.8:
            stability_multiplier += 0.03
        elif expense_pattern < 0.5:
            stability_multiplier -= 0.05

    # STEP 10: Apply fraud and trust adjustments
    fraud_multiplier = 1.0
    if fraud_probability > 0.5:
        fraud_multiplier = 0.0  # No eligibility for high fraud
    elif fraud_probability > 0.3:
        fraud_multiplier = 0.50
    elif fraud_probability > 0.15:
        fraud_multiplier = 0.80

    trust_multiplier = 1.0
    if trust_score is not None:
        if trust_score < 0.3:
            trust_multiplier = 0.0
        elif trust_score < 0.5:
            trust_multiplier = 0.60
        elif trust_score < 0.7:
            trust_multiplier = 0.85

    # STEP 11: Apply verification status adjustment
    verification_multiplier = 1.0
    if verification_status in ['VERIFIED']:
        verification_multiplier = 1.0
    elif verification_status in ['PARTIAL']:
        verification_multiplier = 0.75
    elif verification_status in ['INCOMPLETE', 'PENDING']:
        verification_multiplier = 0.50
    elif verification_status in ['FAILED']:
        verification_multiplier = 0.20

    # STEP 12: Calculate final eligible amount
    eligible_amount = (
        raw_eligible_amount
        * score_multiplier
        * tenure_multiplier
        * stability_multiplier
        * fraud_multiplier
        * trust_multiplier
        * verification_multiplier
    )

    # Apply decision override
    if decision == 'REJECTED':
        eligible_amount = 0
    elif decision == 'REVIEW':
        eligible_amount = eligible_amount * 0.70  # Cap at 70% for review cases

    # Round to nearest 100
    eligible_amount = max(0, round(eligible_amount / 100) * 100)

    # STEP 13: Calculate monthly EMI estimate (for display)
    monthly_emi = round(eligible_amount / 12, 2) if eligible_amount > 0 else 0

    # STEP 14: Generate improvement suggestions
    suggestions = _generate_improvement_suggestions(
        credit_score=credit_score,
        effective_income=effective_income,
        effective_expense=effective_expense,
        savings_ratio=savings_ratio,
        job_tenure=job_tenure,
        employment_type=employment_type,
        income_stability=income_stability,
        expense_pattern=expense_pattern,
        trust_score=trust_score,
        fraud_probability=fraud_probability,
        verification_status=verification_status,
        eligible_amount=eligible_amount,
        max_dti=max_dti,
    )

    # STEP 15: Calculate potential increase amounts
    potential_increase = _calculate_potential_increase(
        effective_income=effective_income,
        effective_expense=effective_expense,
        savings_ratio=savings_ratio,
        credit_score=credit_score,
        income_factor=income_factor,
        score_multiplier=score_multiplier,
        tenure_multiplier=tenure_multiplier,
        stability_multiplier=stability_multiplier,
        eligible_amount=eligible_amount,
    )

    return {
        'eligible_loan_amount': eligible_amount,
        'monthly_emi_estimate': monthly_emi,
        'effective_income': round(effective_income, 2),
        'effective_expense': round(effective_expense, 2),
        'disposable_income': round(disposable_income, 2),
        'savings_ratio': round(savings_ratio, 4),
        'max_dti_ratio': max_dti,
        'score_multiplier': score_multiplier,
        'income_used': 'verified' if verified_income is not None else 'declared',
        'expense_used': 'verified' if verified_expense is not None else 'declared',
        'improvement_suggestions': suggestions,
        'potential_increase': potential_increase,
    }


def _generate_improvement_suggestions(
    credit_score, effective_income, effective_expense, savings_ratio,
    job_tenure, employment_type, income_stability, expense_pattern,
    trust_score, fraud_probability, verification_status, eligible_amount, max_dti
):
    """Generate actionable suggestions to improve loan eligibility."""
    suggestions = []

    # 1. Expense reduction suggestions
    if savings_ratio < 0.30:
        target_expense = effective_income * 0.70
        reduction_needed = max(0, effective_expense - target_expense)
        if reduction_needed > 0:
            suggestions.append({
                'category': 'Reduce Expenses',
                'priority': 'HIGH',
                'message': f'Reduce monthly expenses by ₹{reduction_needed:,.0f} to achieve a 30% savings ratio.',
                'impact': f'Could increase eligibility by up to ₹{reduction_needed * 12 * max_dti:,.0f}',
                'action_items': [
                    'Review and eliminate non-essential subscriptions',
                    'Reduce dining out and entertainment spending',
                    'Optimize utility bills and insurance premiums',
                    f'Target monthly expenses under ₹{target_expense:,.0f}',
                ],
            })

    if savings_ratio < 0.15:
        suggestions.append({
            'category': 'Critical: Savings Too Low',
            'priority': 'CRITICAL',
            'message': f'Your savings ratio is only {savings_ratio*100:.1f}%. Lenders typically expect at least 20-30%.',
            'impact': 'Low savings ratio significantly reduces loan eligibility and approval chances',
            'action_items': [
                'Create a strict monthly budget',
                'Set up automatic savings of at least 20% of income',
                'Reduce discretionary spending immediately',
            ],
        })

    # 2. Income improvement suggestions
    if effective_income < 5000:
        suggestions.append({
            'category': 'Increase Income',
            'priority': 'HIGH',
            'message': 'Your income level limits loan eligibility. Consider ways to increase your monthly earnings.',
            'impact': 'Every ₹1,000 increase in monthly income can raise loan eligibility significantly',
            'action_items': [
                'Explore freelance or side income opportunities',
                'Negotiate a salary raise at your current job',
                'Develop skills for higher-paying positions',
                'Consider part-time work or consulting',
            ],
        })

    # 3. Employment stability suggestions
    if job_tenure < 1:
        suggestions.append({
            'category': 'Build Employment Stability',
            'priority': 'MEDIUM',
            'message': f'Your job tenure is {job_tenure:.1f} years. Lenders prefer 2+ years of stable employment.',
            'impact': 'Longer tenure improves trust score and unlocks higher loan multipliers',
            'action_items': [
                'Stay at your current job for at least 1-2 more years',
                'Avoid frequent job changes during loan application period',
                'Build a stable career track record',
            ],
        })

    # 4. Verification suggestions
    if verification_status in ['PENDING', 'INCOMPLETE']:
        suggestions.append({
            'category': 'Complete Verification',
            'priority': 'HIGH',
            'message': 'Your documents are not fully verified. Full verification can significantly increase eligibility.',
            'impact': 'Verified documents can increase eligibility by up to 50-100%',
            'action_items': [
                'Upload a clear, recent payslip or salary certificate',
                'Provide 3-6 months of bank statements',
                'Ensure all documents are legible and unedited',
                'Make sure declared values match your documents',
            ],
        })

    # 5. Income stability suggestions
    if income_stability is not None and income_stability < 0.6:
        suggestions.append({
            'category': 'Improve Income Stability',
            'priority': 'MEDIUM',
            'message': f'Your income stability score is {income_stability:.0%}. Consistent income patterns improve eligibility.',
            'impact': 'Stable income can add 5-10% to your loan eligibility',
            'action_items': [
                'Maintain regular salary credits in your bank account',
                'Avoid gaps in income',
                'If self-employed, maintain consistent billing patterns',
                'Set up recurring deposits to show financial discipline',
            ],
        })

    # 6. Expense pattern suggestions
    if expense_pattern is not None and expense_pattern < 0.5:
        suggestions.append({
            'category': 'Regularize Expense Pattern',
            'priority': 'LOW',
            'message': f'Your spending pattern is irregular (score: {expense_pattern:.0%}). Regular patterns indicate financial discipline.',
            'impact': 'Regular expense patterns can improve risk assessment by 3-5%',
            'action_items': [
                'Pay bills on fixed dates each month',
                'Set up auto-payments for recurring obligations',
                'Avoid large, sporadic spending spikes',
            ],
        })

    # 7. Credit score improvement
    if credit_score < 650:
        suggestions.append({
            'category': 'Improve Credit Score',
            'priority': 'HIGH',
            'message': f'Your credit score of {credit_score} is below the preferred threshold of 700+.',
            'impact': f'Improving to 700+ could increase eligibility by {((1.0 / max(0.45, _get_score_multiplier(credit_score))) - 1) * 100:.0f}%',
            'action_items': [
                'Ensure timely payment of all existing obligations',
                'Reduce your expense-to-income ratio',
                'Provide complete and verified documentation',
                'Maintain a savings ratio above 30%',
            ],
        })

    # 8. Fraud/trust concerns
    if fraud_probability > 0.15:
        suggestions.append({
            'category': 'Address Verification Concerns',
            'priority': 'CRITICAL',
            'message': 'Potential discrepancies were flagged. Ensure all submitted data is accurate.',
            'impact': 'Resolving discrepancies can restore full eligibility',
            'action_items': [
                'Ensure declared income matches your payslip exactly',
                'Upload original, unedited documents only',
                'Verify that your name and employer details are consistent',
                'Contact support if data was entered incorrectly',
            ],
        })

    # If no suggestions (great profile), provide positive feedback
    if not suggestions:
        suggestions.append({
            'category': 'Strong Financial Profile',
            'priority': 'INFO',
            'message': 'Your profile is strong. Maintain your current financial habits to keep high eligibility.',
            'impact': 'No critical improvements needed',
            'action_items': [
                'Continue maintaining a healthy savings ratio',
                'Keep your employment stable',
                'Consider applying for a higher loan amount',
            ],
        })

    return suggestions


def _calculate_potential_increase(
    effective_income, effective_expense, savings_ratio, credit_score,
    income_factor, score_multiplier, tenure_multiplier, stability_multiplier,
    eligible_amount,
):
    """Calculate how much more the user could be eligible for with improvements."""
    potential = {}

    # What if expenses reduced by 20%?
    reduced_expense = effective_expense * 0.80
    new_disposable = effective_income - reduced_expense
    new_savings_ratio = new_disposable / max(effective_income, 1)
    if new_savings_ratio > savings_ratio:
        new_base = min(new_disposable * 0.50 * 12, effective_income * income_factor)
        new_amount = new_base * score_multiplier * tenure_multiplier * stability_multiplier
        increase = max(0, round((new_amount - eligible_amount) / 100) * 100)
        if increase > 0:
            potential['reduce_expenses_20pct'] = {
                'description': 'If you reduce expenses by 20%',
                'new_eligible_amount': round(new_amount / 100) * 100,
                'increase_amount': increase,
                'new_monthly_expense': round(reduced_expense, 2),
            }

    # What if income increased by 20%?
    increased_income = effective_income * 1.20
    new_disposable_inc = increased_income - effective_expense
    if new_disposable_inc > 0:
        new_base_inc = min(new_disposable_inc * 0.50 * 12, increased_income * income_factor)
        new_amount_inc = new_base_inc * score_multiplier * tenure_multiplier * stability_multiplier
        increase_inc = max(0, round((new_amount_inc - eligible_amount) / 100) * 100)
        if increase_inc > 0:
            potential['increase_income_20pct'] = {
                'description': 'If your income increases by 20%',
                'new_eligible_amount': round(new_amount_inc / 100) * 100,
                'increase_amount': increase_inc,
                'new_monthly_income': round(increased_income, 2),
            }

    # What if credit score improved to 750?
    if credit_score < 750:
        better_score_mult = 1.10  # Multiplier for 750+ score
        potential_amount_score = eligible_amount * (better_score_mult / max(score_multiplier, 0.25))
        increase_score = max(0, round((potential_amount_score - eligible_amount) / 100) * 100)
        if increase_score > 0:
            potential['improve_score_to_750'] = {
                'description': 'If your credit score improves to 750+',
                'new_eligible_amount': round(potential_amount_score / 100) * 100,
                'increase_amount': increase_score,
            }

    return potential


def _get_score_multiplier(credit_score):
    """Helper to get score multiplier."""
    for threshold, multiplier in SCORE_TIERS:
        if credit_score >= threshold:
            return multiplier
    return 0.25
