"""
Bank Statement Parser for Financial Verification
Extracts transaction data and computes verified income/expenses
"""

import re
from datetime import datetime
from collections import defaultdict


def parse_bank_statement(ocr_text):
    """
    Parse bank statement OCR text and extract financial metrics
    
    Returns:
        dict: {
            'total_credits': float,
            'total_debits': float,
            'monthly_avg_credits': float,
            'monthly_avg_debits': float,
            'recurring_payments': list,
            'transaction_count': int,
            'income_stability_score': float,
            'expense_pattern_score': float
        }
    """
    
    if not ocr_text or len(ocr_text) < 50:
        return None
    
    # Extract all transactions
    transactions = extract_transactions(ocr_text)
    
    if not transactions:
        return None
    
    # Separate credits and debits
    credits = [t for t in transactions if t['type'] == 'credit']
    debits = [t for t in transactions if t['type'] == 'debit']
    
    # Calculate totals
    total_credits = sum(t['amount'] for t in credits)
    total_debits = sum(t['amount'] for t in debits)
    
    # Estimate monthly period (assume 1-3 months of data)
    months_covered = estimate_months_covered(transactions)
    
    # Calculate monthly averages
    monthly_avg_credits = total_credits / max(months_covered, 1)
    monthly_avg_debits = total_debits / max(months_covered, 1)
    
    # Detect recurring payments
    recurring_payments = detect_recurring_payments(debits)
    
    # Calculate stability scores
    income_stability = calculate_income_stability(credits)
    expense_pattern = calculate_expense_pattern(debits)
    
    return {
        'total_credits': round(total_credits, 2),
        'total_debits': round(total_debits, 2),
        'monthly_avg_credits': round(monthly_avg_credits, 2),
        'monthly_avg_debits': round(monthly_avg_debits, 2),
        'recurring_payments': recurring_payments,
        'transaction_count': len(transactions),
        'income_stability_score': round(income_stability, 2),
        'expense_pattern_score': round(expense_pattern, 2),
        'months_covered': months_covered
    }


def extract_transactions(text):
    """Extract transaction amounts and types from OCR text"""
    transactions = []
    
    # Pattern 1: Amount with Cr/Dr indicator
    pattern1 = r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(Cr|Dr|Credit|Debit)'
    matches1 = re.finditer(pattern1, text, re.IGNORECASE)
    
    for match in matches1:
        amount_str = match.group(1).replace(',', '')
        trans_type = match.group(2).lower()
        
        try:
            amount = float(amount_str)
            if 10 <= amount <= 10000000:  # Reasonable transaction range
                t_type = 'credit' if 'cr' in trans_type else 'debit'
                transactions.append({
                    'amount': amount,
                    'type': t_type
                })
        except ValueError:
            continue
    
    # Pattern 2: Debit/Credit columns (common in statements)
    # Look for amounts in debit/credit context
    lines = text.split('\n')
    for line in lines:
        # Check if line contains transaction indicators
        if any(keyword in line.lower() for keyword in ['debit', 'credit', 'withdrawal', 'deposit']):
            amounts = re.findall(r'\b(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\b', line)
            for amount_str in amounts:
                try:
                    amount = float(amount_str.replace(',', ''))
                    if 10 <= amount <= 10000000:
                        # Determine type based on keywords
                        if any(kw in line.lower() for kw in ['credit', 'deposit', 'salary', 'transfer in']):
                            t_type = 'credit'
                        else:
                            t_type = 'debit'
                        
                        transactions.append({
                            'amount': amount,
                            'type': t_type
                        })
                except ValueError:
                    continue
    
    # Pattern 3: Fallback - large numbers likely transactions
    if len(transactions) < 5:
        amounts = re.findall(r'\b(\d{4,}(?:,\d{3})*(?:\.\d{2})?)\b', text)
        for i, amount_str in enumerate(amounts[:20]):  # Limit to 20 transactions
            try:
                amount = float(amount_str.replace(',', ''))
                if 100 <= amount <= 10000000:
                    # Alternate between credit and debit as heuristic
                    t_type = 'credit' if i % 2 == 0 else 'debit'
                    transactions.append({
                        'amount': amount,
                        'type': t_type
                    })
            except ValueError:
                continue
    
    return transactions


def estimate_months_covered(transactions):
    """Estimate how many months of data the statement covers"""
    # Heuristic: Assume 10-30 transactions per month
    trans_count = len(transactions)
    
    if trans_count < 10:
        return 1
    elif trans_count < 30:
        return 1
    elif trans_count < 60:
        return 2
    else:
        return 3


def detect_recurring_payments(debits):
    """Detect recurring payment patterns"""
    if not debits:
        return []
    
    # Group similar amounts (within 5% tolerance)
    amount_groups = defaultdict(list)
    
    for debit in debits:
        amount = debit['amount']
        # Find matching group
        found_group = False
        for key_amount in list(amount_groups.keys()):
            if abs(amount - key_amount) / max(amount, key_amount) < 0.05:
                amount_groups[key_amount].append(amount)
                found_group = True
                break
        
        if not found_group:
            amount_groups[amount].append(amount)
    
    # Recurring payments are amounts that appear 2+ times
    recurring = []
    for key_amount, amounts in amount_groups.items():
        if len(amounts) >= 2:
            recurring.append({
                'amount': round(key_amount, 2),
                'frequency': len(amounts)
            })
    
    return recurring[:5]  # Return top 5


def calculate_income_stability(credits):
    """Calculate income stability score (0-1)"""
    if not credits or len(credits) < 2:
        return 0.5
    
    amounts = [c['amount'] for c in credits]
    
    # Calculate coefficient of variation
    mean_amount = sum(amounts) / len(amounts)
    
    if mean_amount == 0:
        return 0.5
    
    variance = sum((x - mean_amount) ** 2 for x in amounts) / len(amounts)
    std_dev = variance ** 0.5
    cv = std_dev / mean_amount
    
    # Lower CV = higher stability
    # CV < 0.2 = very stable (score 1.0)
    # CV > 1.0 = very unstable (score 0.3)
    if cv < 0.2:
        stability = 1.0
    elif cv > 1.0:
        stability = 0.3
    else:
        stability = 1.0 - (cv * 0.7)
    
    return max(0.3, min(1.0, stability))


def calculate_expense_pattern(debits):
    """Calculate expense pattern regularity score (0-1)"""
    if not debits or len(debits) < 3:
        return 0.5
    
    amounts = [d['amount'] for d in debits]
    
    # Check for recurring patterns
    recurring_count = 0
    amount_set = set()
    
    for amount in amounts:
        # Check if similar amount exists
        for existing in amount_set:
            if abs(amount - existing) / max(amount, existing) < 0.1:
                recurring_count += 1
                break
        amount_set.add(amount)
    
    # Higher recurring ratio = more regular pattern
    recurring_ratio = recurring_count / len(amounts)
    
    # Score: 0.5 base + 0.5 * recurring_ratio
    pattern_score = 0.5 + (0.5 * recurring_ratio)
    
    return max(0.3, min(1.0, pattern_score))
