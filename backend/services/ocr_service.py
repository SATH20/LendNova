"""
OCR Service - Core Document Intelligence Engine
High-accuracy extraction of structured financial data from payslips,
bank statements, and other document formats. Handles diverse layouts,
patterns and formats with multi-stage parsing and confidence scoring.
"""

import os
import re
import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
from pdf2image import convert_from_path
from utils.helpers import clean_text
from difflib import SequenceMatcher


# ──────────────────────────────────────────────────
#  Stage 0 — Image Pre-processing for better OCR
# ──────────────────────────────────────────────────

def preprocess_image(image):
    """Apply image preprocessing to improve OCR accuracy."""
    # Convert to grayscale
    image = image.convert('L')

    # Increase contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)

    # Increase sharpness
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(2.0)

    # Apply slight noise reduction
    image = image.filter(ImageFilter.MedianFilter(size=3))

    # Binarize (threshold) for cleaner text
    threshold = 160
    image = image.point(lambda p: 255 if p > threshold else 0)

    return image


def extract_text_from_image(image_path, config=None):
    """
    Extract structured financial data from document images with high accuracy.

    Supports:
    - Payslips (salary slips, pay stubs)
    - Bank statements
    - Income certificates
    - PDF and image formats (PNG, JPG, JPEG)

    Returns:
        dict: Extracted data with confidence scores
    """
    if config and getattr(config, "TESSERACT_CMD", None):
        if not os.path.exists(config.TESSERACT_CMD):
            raise FileNotFoundError("Tesseract executable not found")
        pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD

    ext = os.path.splitext(image_path)[1].lower()

    # Multi-pass OCR for better accuracy
    texts = []

    if ext == ".pdf":
        pages = convert_from_path(image_path)
        for page in pages:
            # Pass 1: Raw OCR
            text1 = pytesseract.image_to_string(page)
            texts.append(text1)
            # Pass 2: With preprocessing
            preprocessed = preprocess_image(page)
            text2 = pytesseract.image_to_string(preprocessed)
            if len(text2.strip()) > len(text1.strip()):
                texts[-1] = text2
    else:
        img = Image.open(image_path)
        # Pass 1: Raw OCR
        text1 = pytesseract.image_to_string(img)
        texts.append(text1)
        # Pass 2: With preprocessing
        preprocessed = preprocess_image(img)
        text2 = pytesseract.image_to_string(preprocessed)
        if len(text2.strip()) > len(text1.strip()):
            texts[-1] = text2
        # Pass 3: With different PSM mode for tabular layouts
        try:
            text3 = pytesseract.image_to_string(img, config='--psm 6')
            if len(text3.strip()) > len(texts[-1].strip()):
                texts.append(text3)
        except Exception:
            pass

    text = " ".join(texts)
    text = clean_text(text)

    # Detect document type
    doc_type = detect_document_type(text)

    # Smart extraction with confidence scoring
    extracted_fields = smart_extract_fields(text, doc_type)

    # Extract bank statement data if applicable
    bank_data = None
    if doc_type == 'bank_statement':
        bank_data = extract_bank_statement_data(text)

    extracted_data = {
        "raw_text": text,
        "name": extracted_fields.get("name"),
        "income": extracted_fields.get("income"),
        "employer": extracted_fields.get("employer"),
        "extraction_confidence": extracted_fields.get("confidence", 0.0),
        "document_type_detected": doc_type,
        "bank_data": bank_data,
        "all_amounts": extracted_fields.get("all_amounts", []),
        "all_dates": extracted_fields.get("all_dates", []),
    }

    return extracted_data


# ──────────────────────────────────────────────────
#  Stage 1 — Document Type Detection
# ──────────────────────────────────────────────────

def detect_document_type(text):
    """Detect the type of document from OCR text."""
    text_lower = text.lower()

    payslip_indicators = [
        'payslip', 'pay slip', 'salary slip', 'pay stub',
        'net pay', 'gross pay', 'basic salary', 'earnings',
        'deductions', 'employee id', 'emp id', 'employee name',
        'hra', 'provident fund', 'pf', 'professional tax',
        'take home', 'ctc', 'gross salary', 'net salary',
        'pay period', 'pay date', 'department', 'designation',
    ]

    bank_statement_indicators = [
        'bank statement', 'account statement', 'statement of account',
        'account number', 'account no', 'a/c no',
        'opening balance', 'closing balance',
        'credit', 'debit', 'withdrawal', 'deposit',
        'transaction', 'transfer', 'neft', 'rtgs', 'imps', 'upi',
        'ifsc', 'branch', 'cheque', 'atm',
    ]

    payslip_score = sum(1 for indicator in payslip_indicators if indicator in text_lower)
    bank_score = sum(1 for indicator in bank_statement_indicators if indicator in text_lower)

    if payslip_score > bank_score and payslip_score >= 2:
        return 'payslip'
    elif bank_score > payslip_score and bank_score >= 2:
        return 'bank_statement'
    elif payslip_score >= 1:
        return 'payslip'
    elif bank_score >= 1:
        return 'bank_statement'
    else:
        return 'unknown'


# ──────────────────────────────────────────────────
#  Stage 2 — Text Normalization
# ──────────────────────────────────────────────────

def normalize_text(text):
    """Stage 1: Text normalization - split into lines and clean"""
    # First split by newlines
    lines = text.split('\n')

    # Also split by multiple spaces (common in OCR output)
    all_lines = []
    for line in lines:
        # Split by 2 or more spaces (indicates column separation)
        parts = re.split(r'\s{2,}', line)
        all_lines.extend(parts)

    # Further split by common label patterns to break up long lines
    further_split = []
    label_patterns = [
        r'(?=\b(?:Employee|Name|Department|Designation|Date|Pay|Bank|Days|Earnings|Deductions|Total|Net|Gross|Basic|HRA|PF|Tax|Balance|Account|Credit|Debit)\b)',
    ]

    for line in all_lines:
        # Try splitting by label patterns
        split_done = False
        for pattern in label_patterns:
            parts = re.split(pattern, line, flags=re.IGNORECASE)
            if len(parts) > 1:
                further_split.extend([p.strip() for p in parts if p.strip()])
                split_done = True
                break

        if not split_done:
            further_split.append(line)

    normalized_lines = []
    for line in further_split:
        # Remove excessive whitespace
        line = ' '.join(line.split())
        # Remove special characters but keep alphanumeric, spaces, and common punctuation
        line = re.sub(r'[^\w\s\.,\-\$₹€£¥@#:()\/]', ' ', line)
        line = line.strip()
        if line and len(line) > 2:  # Only keep non-empty lines with substance
            normalized_lines.append(line)

    return normalized_lines


# ──────────────────────────────────────────────────
#  Stage 3 — Keyword Matching
# ──────────────────────────────────────────────────

def keyword_similarity(text, keyword):
    """Calculate similarity between text and keyword"""
    text_lower = text.lower()
    keyword_lower = keyword.lower()

    # Exact match
    if keyword_lower in text_lower:
        return 1.0

    # Fuzzy match
    return SequenceMatcher(None, text_lower, keyword_lower).ratio()


def find_keyword_line(lines, keywords, threshold=0.6):
    """Stage 2: Find line containing any of the keywords"""
    best_match = (None, None, 0.0)
    for i, line in enumerate(lines):
        for keyword in keywords:
            similarity = keyword_similarity(line, keyword)
            if similarity >= threshold and similarity > best_match[2]:
                best_match = (i, line, similarity)
                if similarity >= 1.0:
                    return best_match
    return best_match


def find_all_keyword_lines(lines, keywords, threshold=0.6):
    """Find ALL lines containing any of the keywords (for multi-match extraction)."""
    matches = []
    for i, line in enumerate(lines):
        for keyword in keywords:
            similarity = keyword_similarity(line, keyword)
            if similarity >= threshold:
                matches.append((i, line, similarity, keyword))
                break
    return matches


# ──────────────────────────────────────────────────
#  Stage 4 — Value Extraction
# ──────────────────────────────────────────────────

def extract_value_from_context(lines, keyword_index, value_type="text"):
    """Stage 3: Extract value from context window around keyword"""
    if keyword_index is None:
        return None

    # Try same line first
    line = lines[keyword_index]

    if value_type == "name":
        value = extract_name_from_line(line)
        if value:
            return value
        # Try next line
        if keyword_index + 1 < len(lines):
            value = extract_name_from_line(lines[keyword_index + 1])
            if value:
                return value
        # Try previous line
        if keyword_index - 1 >= 0:
            value = extract_name_from_line(lines[keyword_index - 1])
            if value:
                return value

    elif value_type == "amount":
        value = extract_amount_from_line(line)
        if value:
            return value
        # Try next line
        if keyword_index + 1 < len(lines):
            value = extract_amount_from_line(lines[keyword_index + 1])
            if value:
                return value

    elif value_type == "company":
        value = extract_company_from_line(line)
        if value:
            return value
        # Try next line
        if keyword_index + 1 < len(lines):
            value = extract_company_from_line(lines[keyword_index + 1])
            if value:
                return value
        # Try previous line
        if keyword_index - 1 >= 0:
            value = extract_company_from_line(lines[keyword_index - 1])
            if value:
                return value

    return None


def extract_name_from_line(line):
    """Extract name from a line using multiple patterns"""
    # Remove common keywords first
    cleaned = re.sub(r'\b(name|employee|emp|worker|staff|sno|id|number|mr|mrs|ms|dr)\b', '', line, flags=re.IGNORECASE)
    cleaned = re.sub(r'[:\-]', ' ', cleaned)  # Remove colons and hyphens after labels
    cleaned = cleaned.strip()

    # Pattern 1: After colon/dash (common: "Name: John Doe")
    colon_match = re.search(r'[:\-]\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})', line)
    if colon_match:
        name = colon_match.group(1).strip()
        if 3 <= len(name) <= 50 and name.lower() not in ['dream group', 'pay slip', 'salary slip']:
            return name

    # Pattern 2: Two or three capitalized words in sequence
    pattern = r'\b([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b'
    matches = re.findall(pattern, cleaned)

    for match in matches:
        name = match.strip()
        words = name.split()
        # Valid name: 2-3 words, reasonable length, not common non-names
        if (2 <= len(words) <= 3 and
            3 <= len(name) <= 50 and
            name.lower() not in ['dream group', 'pay slip', 'salary slip',
                                  'net pay', 'gross pay', 'basic salary',
                                  'total earnings', 'total deductions']):
            return name

    # Pattern 3: Fallback - any capitalized words after cleaning
    words = cleaned.split()
    cap_words = [w for w in words if w and len(w) > 1 and w[0].isupper()]

    if 2 <= len(cap_words) <= 3:
        name = ' '.join(cap_words[:3])
        if (3 <= len(name) <= 50 and
            name.lower() not in ['dream group', 'pay slip', 'salary slip',
                                  'net pay', 'gross pay', 'basic salary']):
            return name

    return None


def extract_amount_from_line(line):
    """Stage 4: Extract amount using multi-pattern detection with high accuracy"""
    # Remove currency symbols and clean
    line_cleaned = re.sub(r'[₹$€£¥]', '', line)
    # Remove common non-amount text
    line_cleaned = re.sub(r'\b(days|months|years|hrs|hours|min|page|no)\b', '', line_cleaned, flags=re.IGNORECASE)

    # Multiple amount patterns (ordered by specificity)
    patterns = [
        r'\b(\d{1,3}(?:,\d{3})*\.\d{2})\b',     # 90,148.00 (with comma and decimals)
        r'\b(\d{4,}(?:\.\d{2})?)\b',               # 90148 or 90148.00 (large number)
        r'\b(\d{1,3}(?:,\d{3})+)\b',               # 90,148 (comma-separated)
        r'\b(\d{1,3}(?:,\d{2})+(?:\.\d{2})?)\b',   # Indian format: 90,14,800.00
    ]

    amounts = []
    for pattern in patterns:
        matches = re.findall(pattern, line_cleaned)
        for match in matches:
            try:
                amount = float(match.replace(',', ''))
                if 500 <= amount <= 10000000:
                    amounts.append(amount)
            except ValueError:
                continue

    # Return largest amount found (likely the main salary/net pay)
    return max(amounts) if amounts else None


def extract_all_amounts_from_line(line):
    """Extract ALL monetary amounts from a line."""
    line_cleaned = re.sub(r'[₹$€£¥]', '', line)
    amounts = []

    patterns = [
        r'\b(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\b',
        r'\b(\d{4,}(?:\.\d{2})?)\b',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, line_cleaned)
        for match in matches:
            try:
                amount = float(match.replace(',', ''))
                if 10 <= amount <= 10000000:
                    amounts.append(amount)
            except ValueError:
                continue

    return sorted(set(amounts))


def extract_company_from_line(line):
    """Extract company name from a line with improved patterns."""
    # Try after colon pattern first (e.g., "Company: ABC Corp")
    colon_match = re.search(r'(?:company|employer|organization|firm|issued by)\s*[:\-]\s*(.+)', line, re.IGNORECASE)
    if colon_match:
        company = colon_match.group(1).strip()
        # Take first 2-4 meaningful words
        words = company.split()[:4]
        company = ' '.join(words)
        if 2 <= len(company) <= 60:
            return company

    # Remove common keywords
    line = re.sub(r'\b(company|employer|organization|group|ltd|limited|inc|corp|payslip|pay slip|pvt|private)\b', '', line, flags=re.IGNORECASE)
    line = re.sub(r'[:\-]', ' ', line)
    line = line.strip()

    # Pattern: Take first 1-3 capitalized words
    words = line.split()
    if words:
        company_words = []
        for word in words[:4]:  # Check first 4 words
            if word and len(word) > 1:
                # Accept capitalized or all-caps words
                if word[0].isupper() or word.isupper():
                    company_words.append(word)
                else:
                    break  # Stop at first non-capitalized word

            if len(company_words) >= 3:  # Limit to 3 words for company name
                break

        if company_words:
            company = ' '.join(company_words)
            if 2 <= len(company) <= 60:
                return company

    return None


# ──────────────────────────────────────────────────
#  Stage 5 — Fallback Heuristics
# ──────────────────────────────────────────────────

def fallback_extract_income(lines, doc_type='unknown'):
    """Stage 5: Fallback heuristic - find largest monetary value with context"""
    all_amounts = []

    # Priority keywords for income context
    income_context_keywords = [
        'net', 'salary', 'pay', 'income', 'total', 'gross', 'earning',
        'credit', 'deposit', 'take home', 'amount',
    ]

    for line in lines:
        amounts = extract_amount_from_line(line)
        if amounts:
            # Boost priority if line has income-related context
            has_context = any(kw in line.lower() for kw in income_context_keywords)
            all_amounts.append((amounts, has_context))

    if not all_amounts:
        return None

    # Prefer amounts with income context
    context_amounts = [a[0] for a in all_amounts if a[1]]
    if context_amounts:
        return max(context_amounts)

    # Fallback: return largest amount found
    return max(a[0] for a in all_amounts)


def fallback_extract_employer(lines):
    """Stage 5: Fallback heuristic - scan top lines for company name"""
    # Check first 5 lines for company-like names
    for line in lines[:5]:
        # Look for lines with capitalized words before common document keywords
        if any(keyword in line.lower() for keyword in ['payslip', 'pay slip', 'salary slip', 'pay stub']):
            # Extract text before these keywords
            parts = re.split(r'\b(payslip|pay slip|salary slip|pay stub)\b', line, flags=re.IGNORECASE)
            if parts[0]:
                text = parts[0].strip()
                segments = re.split(r',', text)
                if segments:
                    first_segment = segments[0].strip()
                    words = first_segment.split()

                    company_words = []
                    for word in words[:3]:
                        if word and len(word) > 1 and (word[0].isupper() or word.isupper()):
                            company_words.append(word)

                    if len(company_words) >= 1:
                        company = ' '.join(company_words)
                        if 2 <= len(company) <= 60:
                            return company

        # Try extracting company from line (first 2 words only)
        words = line.split()
        company_words = []
        for word in words[:3]:
            if word and len(word) > 1 and (word[0].isupper() or word.isupper()):
                company_words.append(word)

        if len(company_words) >= 2:
            company = ' '.join(company_words)
            if 3 <= len(company) <= 60:
                return company

    return None


# ──────────────────────────────────────────────────
#  Stage 6 — Smart Extraction Engine
# ──────────────────────────────────────────────────

def smart_extract_fields(text, doc_type='unknown'):
    """Main smart extraction engine with multi-stage parsing"""
    # Stage 1: Normalize text
    lines = normalize_text(text)

    if not lines:
        return {"name": None, "income": None, "employer": None, "confidence": 0.0}

    # Stage 2: Keyword dictionaries (expanded for higher accuracy)
    name_keywords = [
        "name", "employee name", "emp name", "worker", "staff name",
        "employee", "emp", "person", "account holder", "holder name",
        "applicant name", "borrower name", "customer name",
    ]

    # Prioritize net pay keywords first (more important for loan assessment)
    income_keywords_priority = [
        "net pay", "net salary", "take home", "take home pay",
        "net amount", "amount payable", "total net pay",
    ]

    income_keywords_secondary = [
        "income", "total earnings", "gross pay", "gross salary", "salary",
        "pay", "amount", "total pay", "basic pay", "monthly salary",
        "total amount", "total credit", "earnings",
    ]

    employer_keywords = [
        "company", "employer", "organization", "group", "ltd",
        "limited", "corporation", "corp", "inc", "firm",
        "issued by", "prepared by", "company name",
    ]

    # Extract fields using keyword search (prioritize net pay)
    name_idx, name_line, name_conf = find_keyword_line(lines, name_keywords)

    # Try priority income keywords first
    income_idx, income_line, income_conf = find_keyword_line(lines, income_keywords_priority)
    if income_idx is None:
        income_idx, income_line, income_conf = find_keyword_line(lines, income_keywords_secondary)

    employer_idx, employer_line, employer_conf = find_keyword_line(lines, employer_keywords)

    # Stage 3: Context window extraction
    name = extract_value_from_context(lines, name_idx, "name")
    income = extract_value_from_context(lines, income_idx, "amount")
    employer = extract_value_from_context(lines, employer_idx, "company")

    # Stage 5: Fallback heuristics
    if not income:
        income = fallback_extract_income(lines, doc_type)

    if not employer:
        employer = fallback_extract_employer(lines)

    # Extract all amounts for additional analysis
    all_amounts = []
    for line in lines:
        amounts = extract_all_amounts_from_line(line)
        all_amounts.extend(amounts)
    all_amounts = sorted(set(all_amounts), reverse=True)[:10]

    # Extract all dates
    all_dates = extract_all_dates(text)

    # Stage 6: Calculate extraction confidence
    fields_attempted = 3
    fields_extracted = sum([
        1 if name else 0,
        1 if income else 0,
        1 if employer else 0
    ])

    # Base confidence from field extraction
    base_confidence = fields_extracted / fields_attempted

    # Boost confidence if amounts were found in context
    if income and income_conf >= 0.8:
        base_confidence = min(1.0, base_confidence + 0.1)

    # Boost confidence if document type was detected
    if doc_type in ['payslip', 'bank_statement']:
        base_confidence = min(1.0, base_confidence + 0.05)

    return {
        "name": name,
        "income": income,
        "employer": employer,
        "confidence": round(base_confidence, 2),
        "all_amounts": all_amounts,
        "all_dates": all_dates,
    }


# ──────────────────────────────────────────────────
#  Stage 7 — Bank Statement Data Extraction
# ──────────────────────────────────────────────────

def extract_bank_statement_data(text):
    """Extract structured data from bank statements with high accuracy."""
    text_lower = text.lower()

    result = {
        'account_number': None,
        'opening_balance': None,
        'closing_balance': None,
        'total_credits': 0,
        'total_debits': 0,
        'transaction_count': 0,
    }

    # Extract account number
    acc_patterns = [
        r'(?:account\s*(?:no|number|#)?|a/c\s*(?:no)?)\s*[:\-]?\s*(\d{8,18})',
        r'\b(\d{10,18})\b',
    ]
    for pattern in acc_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result['account_number'] = match.group(1)
            break

    # Extract balances
    balance_patterns = [
        (r'opening\s*balance\s*[:\-]?\s*[\₹$]?\s*([\d,]+(?:\.\d{2})?)', 'opening_balance'),
        (r'closing\s*balance\s*[:\-]?\s*[\₹$]?\s*([\d,]+(?:\.\d{2})?)', 'closing_balance'),
    ]
    for pattern, key in balance_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                result[key] = float(match.group(1).replace(',', ''))
            except ValueError:
                pass

    return result


def extract_all_dates(text):
    """Extract all dates from text."""
    date_patterns = [
        r'(\d{2}[/\-]\d{2}[/\-]\d{4})',
        r'(\d{4}[/\-]\d{2}[/\-]\d{2})',
        r'(\d{2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})',
    ]

    dates = []
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        dates.extend(matches)

    return dates[:10]  # Return top 10 dates


# ──────────────────────────────────────────────────
#  Legacy functions kept for backward compatibility
# ──────────────────────────────────────────────────

def extract_field(text, pattern):
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return None
    if match.lastindex and match.lastindex > 1:
        return match.group(2).strip()
    return match.group(1).strip()


def extract_amount(text, pattern):
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        amount_str = match.group(match.lastindex).replace(",", "")
        try:
            return float(amount_str)
        except ValueError:
            return None
    return None
