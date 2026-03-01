"""
Verification Engine - Employment-Type Adaptive Verification Router
Routes verification based on employment type and validates financial data
"""

from services.bank_statement_parser import parse_bank_statement
from services.identity_verification import verify_identity


def verification_router(assessment_data, ocr_data_payslip=None, ocr_data_bank=None, file_path_payslip=None):
    employment_type = assessment_data.get('employment_type', '').lower()
    declared_income = float(assessment_data.get('income', 0))
    declared_expense = float(assessment_data.get('expenses', 0))
    
    result = {
        'employment_type': employment_type,
        'declared_income': declared_income,
        'declared_expense': declared_expense,
        'verified_income': None,
        'verified_expense': None,
        'verification_method': None,
        'verification_flags': [],
        'trust_score': 0.0,
        'verification_status': 'PENDING',
        'assessment_stage': 'PRELIMINARY',
        'income_verification_score': 0.0,
        'expense_verification_score': 0.0,
        'ocr_confidence': 0.0,
        'identity_consistency': 0.0,
        'income_stability_score': None,
        'expense_pattern_score': None,
    }
    
    if employment_type in ['full-time', 'full time', 'fulltime']:
        return verify_salaried(assessment_data, ocr_data_payslip, ocr_data_bank, file_path_payslip, result)
    elif employment_type in ['self-employed', 'self employed', 'selfemployed']:
        return verify_self_employed(assessment_data, ocr_data_bank, result)
    elif employment_type in ['student']:
        return verify_student(assessment_data, ocr_data_bank, result)
    elif employment_type in ['part-time', 'part time', 'parttime']:
        return verify_part_time(assessment_data, ocr_data_bank, result)
    elif employment_type in ['unemployed']:
        return verify_unemployed(assessment_data, ocr_data_bank, result)
    else:
        return verify_default(assessment_data, ocr_data_payslip, ocr_data_bank, file_path_payslip, result)


def verify_salaried(assessment_data, ocr_payslip, ocr_bank, file_path, result):
    result['verification_method'] = 'SALARIED'
    has_payslip = ocr_payslip and (ocr_payslip.get('income') or ocr_payslip.get('name'))
    has_bank = ocr_bank and ocr_bank.get('raw_text')
    
    if not has_payslip and not has_bank:
        result['verification_flags'].append('Payslip and bank statement required for salaried verification')
        result['verification_status'] = 'INCOMPLETE'
        return result
    
    income_verified = False
    if has_payslip and ocr_payslip.get('income'):
        result['verified_income'] = ocr_payslip['income']
        income_verified = True
        income_gap = abs(result['declared_income'] - result['verified_income'])
        income_gap_pct = income_gap / max(result['declared_income'], 1)
        if income_gap_pct > 0.20:
            result['verification_flags'].append(f'Income mismatch: {income_gap_pct*100:.1f}% difference')
            result['income_verification_score'] = max(0.3, 1.0 - income_gap_pct)
        else:
            result['income_verification_score'] = 1.0
    
    expense_verified = False
    if has_bank:
        bank_data = parse_bank_statement(ocr_bank['raw_text'])
        if bank_data:
            result['verified_expense'] = bank_data['monthly_avg_debits']
            result['income_stability_score'] = bank_data['income_stability_score']
            result['expense_pattern_score'] = bank_data['expense_pattern_score']
            expense_verified = True
            if not income_verified and bank_data['monthly_avg_credits'] > 0:
                result['verified_income'] = bank_data['monthly_avg_credits']
                income_verified = True
                result['verification_flags'].append('Income estimated from bank credits')
                result['income_verification_score'] = 0.7
            expense_gap = abs(result['declared_expense'] - result['verified_expense'])
            expense_gap_pct = expense_gap / max(result['declared_expense'], 1)
            if expense_gap_pct > 0.20:
                result['verification_flags'].append(f'Expense mismatch: {expense_gap_pct*100:.1f}% difference')
                result['expense_verification_score'] = max(0.3, 1.0 - expense_gap_pct)
            else:
                result['expense_verification_score'] = 1.0
    
    result['ocr_confidence'] = 0.8 if (has_payslip and has_bank) else 0.5
    if has_payslip:
        identity_result = verify_identity(assessment_data, ocr_payslip, file_path)
        result['identity_consistency'] = identity_result.get('trust_score', 0.5)
    else:
        result['identity_consistency'] = 0.5
    
    result['trust_score'] = calculate_trust_score(
        result['income_verification_score'],
        result['expense_verification_score'],
        result['ocr_confidence'],
        result['identity_consistency']
    )
    
    if income_verified and expense_verified:
        result['verification_status'] = 'VERIFIED'
        result['assessment_stage'] = 'VERIFIED'
    elif income_verified or expense_verified:
        result['verification_status'] = 'PARTIAL'
        result['assessment_stage'] = 'PARTIAL'
    else:
        result['verification_status'] = 'INCOMPLETE'
    
    return result


def verify_self_employed(assessment_data, ocr_bank, result):
    result['verification_method'] = 'SELF_EMPLOYED'
    has_bank = ocr_bank and ocr_bank.get('raw_text')
    if not has_bank:
        result['verification_flags'].append('Bank statement required for self-employed verification')
        result['verification_status'] = 'INCOMPLETE'
        return result
    bank_data = parse_bank_statement(ocr_bank['raw_text'])
    if not bank_data:
        result['verification_flags'].append('Unable to parse bank statement')
        result['verification_status'] = 'FAILED'
        return result
    result['verified_income'] = bank_data['monthly_avg_credits']
    result['verified_expense'] = bank_data['monthly_avg_debits']
    result['income_stability_score'] = bank_data['income_stability_score']
    result['expense_pattern_score'] = bank_data['expense_pattern_score']
    income_gap_pct = abs(result['declared_income'] - result['verified_income']) / max(result['declared_income'], 1)
    expense_gap_pct = abs(result['declared_expense'] - result['verified_expense']) / max(result['declared_expense'], 1)
    if income_gap_pct > 0.30:
        result['verification_flags'].append(f'Income variability: {income_gap_pct*100:.1f}% difference')
    if expense_gap_pct > 0.30:
        result['verification_flags'].append(f'Expense variability: {expense_gap_pct*100:.1f}% difference')
    result['income_verification_score'] = max(0.5, 1.0 - (income_gap_pct * 0.5))
    result['expense_verification_score'] = max(0.5, 1.0 - (expense_gap_pct * 0.5))
    result['ocr_confidence'] = 0.7
    result['identity_consistency'] = 0.7
    if result['income_stability_score'] < 0.5:
        result['verification_flags'].append('High income variability detected')
    result['trust_score'] = calculate_trust_score(
        result['income_verification_score'],
        result['expense_verification_score'],
        result['ocr_confidence'],
        result['identity_consistency']
    )
    result['verification_status'] = 'VERIFIED'
    result['assessment_stage'] = 'VERIFIED'
    return result


def verify_student(assessment_data, ocr_bank, result):
    result['verification_method'] = 'STUDENT'
    has_bank = ocr_bank and ocr_bank.get('raw_text')
    if has_bank:
        bank_data = parse_bank_statement(ocr_bank['raw_text'])
        if bank_data:
            result['verified_income'] = bank_data['monthly_avg_credits']
            result['verified_expense'] = bank_data['monthly_avg_debits']
            result['income_stability_score'] = bank_data['income_stability_score']
            result['expense_pattern_score'] = bank_data['expense_pattern_score']
            result['income_verification_score'] = 0.6
            result['expense_verification_score'] = 0.8
            result['ocr_confidence'] = 0.7
            result['identity_consistency'] = 0.7
            result['verification_status'] = 'VERIFIED'
            result['assessment_stage'] = 'VERIFIED'
        else:
            result['verification_flags'].append('Bank statement parsing failed')
            result['income_verification_score'] = 0.5
            result['expense_verification_score'] = 0.5
            result['verification_status'] = 'PARTIAL'
    else:
        result['verification_flags'].append('Student assessment - reduced income verification requirement')
        result['income_verification_score'] = 0.5
        result['expense_verification_score'] = 0.6
        result['verification_status'] = 'PARTIAL'
    result['ocr_confidence'] = 0.6
    result['identity_consistency'] = 0.6
    result['trust_score'] = calculate_trust_score(
        result['income_verification_score'],
        result['expense_verification_score'],
        result['ocr_confidence'],
        result['identity_consistency']
    )
    return result


def verify_part_time(assessment_data, ocr_bank, result):
    result['verification_method'] = 'PART_TIME'
    has_bank = ocr_bank and ocr_bank.get('raw_text')
    if not has_bank:
        result['verification_flags'].append('Bank statement recommended for part-time verification')
        result['verification_status'] = 'INCOMPLETE'
        result['income_verification_score'] = 0.4
        result['expense_verification_score'] = 0.4
        result['ocr_confidence'] = 0.5
        result['identity_consistency'] = 0.5
        result['trust_score'] = calculate_trust_score(
            result['income_verification_score'],
            result['expense_verification_score'],
            result['ocr_confidence'],
            result['identity_consistency']
        )
        return result
    bank_data = parse_bank_statement(ocr_bank['raw_text'])
    if bank_data:
        result['verified_income'] = bank_data['monthly_avg_credits']
        result['verified_expense'] = bank_data['monthly_avg_debits']
        result['income_stability_score'] = bank_data['income_stability_score']
        result['expense_pattern_score'] = bank_data['expense_pattern_score']
        if result['income_stability_score'] < 0.6:
            result['verification_flags'].append('High income volatility detected for part-time work')
        income_gap_pct = abs(result['declared_income'] - result['verified_income']) / max(result['declared_income'], 1)
        expense_gap_pct = abs(result['declared_expense'] - result['verified_expense']) / max(result['declared_expense'], 1)
        result['income_verification_score'] = max(0.4, 1.0 - (income_gap_pct * 0.7))
        result['expense_verification_score'] = max(0.5, 1.0 - (expense_gap_pct * 0.7))
        result['ocr_confidence'] = 0.7
        result['identity_consistency'] = 0.7
        result['verification_status'] = 'VERIFIED'
        result['assessment_stage'] = 'VERIFIED'
    else:
        result['verification_flags'].append('Bank statement parsing failed')
        result['verification_status'] = 'PARTIAL'
    result['trust_score'] = calculate_trust_score(
        result['income_verification_score'],
        result['expense_verification_score'],
        result['ocr_confidence'],
        result['identity_consistency']
    )
    return result


def verify_unemployed(assessment_data, ocr_bank, result):
    result['verification_method'] = 'UNEMPLOYED'
    has_bank = ocr_bank and ocr_bank.get('raw_text')
    if has_bank:
        bank_data = parse_bank_statement(ocr_bank['raw_text'])
        if bank_data:
            result['verified_expense'] = bank_data['monthly_avg_debits']
            result['expense_pattern_score'] = bank_data['expense_pattern_score']
            if bank_data['monthly_avg_credits'] > 1000:
                result['verification_flags'].append('Income detected despite unemployed status')
                result['verified_income'] = bank_data['monthly_avg_credits']
    result['income_verification_score'] = 0.3
    result['expense_verification_score'] = 0.6 if has_bank else 0.4
    result['ocr_confidence'] = 0.5
    result['identity_consistency'] = 0.5
    result['verification_status'] = 'PARTIAL'
    result['trust_score'] = calculate_trust_score(
        result['income_verification_score'],
        result['expense_verification_score'],
        result['ocr_confidence'],
        result['identity_consistency']
    )
    return result


def verify_default(assessment_data, ocr_payslip, ocr_bank, file_path, result):
    result['verification_method'] = 'DEFAULT'
    return verify_salaried(assessment_data, ocr_payslip, ocr_bank, file_path, result)


def calculate_trust_score(income_score, expense_score, ocr_conf, identity_conf):
    trust = (
        0.35 * income_score +
        0.35 * expense_score +
        0.15 * ocr_conf +
        0.15 * identity_conf
    )
    return round(max(0.0, min(1.0, trust)), 4)


def get_final_values(verification_result, declared_income, declared_expense):
    final_income = verification_result.get('verified_income') or declared_income
    final_expense = verification_result.get('verified_expense') or declared_expense
    return {
        'final_income': final_income,
        'final_expense': final_expense,
        'used_verified_income': verification_result.get('verified_income') is not None,
        'used_verified_expense': verification_result.get('verified_expense') is not None
    }
