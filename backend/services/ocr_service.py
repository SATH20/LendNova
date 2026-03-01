import os
import re
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from utils.helpers import clean_text
from difflib import SequenceMatcher

def extract_text_from_image(image_path, config=None):
    if config and getattr(config, "TESSERACT_CMD", None):
        if not os.path.exists(config.TESSERACT_CMD):
            raise FileNotFoundError("Tesseract executable not found")
        pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD

    ext = os.path.splitext(image_path)[1].lower()
    if ext == ".pdf":
        pages = convert_from_path(image_path)
        text = " ".join([pytesseract.image_to_string(page) for page in pages])
    else:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
    text = clean_text(text)

    # Smart extraction with confidence scoring
    extracted_fields = smart_extract_fields(text)
    
    extracted_data = {
        "raw_text": text,
        "name": extracted_fields.get("name"),
        "income": extracted_fields.get("income"),
        "employer": extracted_fields.get("employer"),
        "extraction_confidence": extracted_fields.get("confidence", 0.0),
    }

    return extracted_data


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
        r'(?=\b(?:Employee|Name|Department|Designation|Date|Pay|Bank|Days|Earnings|Deductions|Total|Net)\b)',
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
        line = re.sub(r'[^\w\s\.,\-\$₹€£¥@#:()]', ' ', line)
        line = line.strip()
        if line and len(line) > 2:  # Only keep non-empty lines with substance
            normalized_lines.append(line)
    
    return normalized_lines


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
    for i, line in enumerate(lines):
        for keyword in keywords:
            similarity = keyword_similarity(line, keyword)
            if similarity >= threshold:
                return i, line, similarity
    return None, None, 0.0


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
    
    return None


def extract_name_from_line(line):
    """Extract name from a line using multiple patterns"""
    # Remove common keywords first
    cleaned = re.sub(r'\b(name|employee|emp|worker|staff|sno|id|number)\b', '', line, flags=re.IGNORECASE)
    cleaned = cleaned.strip()
    
    # Pattern 1: Two or three capitalized words in sequence
    pattern = r'\b([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b'
    matches = re.findall(pattern, cleaned)
    
    for match in matches:
        name = match.strip()
        words = name.split()
        # Valid name: 2-3 words, reasonable length, not common non-names
        if (2 <= len(words) <= 3 and 
            3 <= len(name) <= 50 and
            name.lower() not in ['dream group', 'pay slip', 'salary slip']):
            return name
    
    # Pattern 2: Fallback - any capitalized words after cleaning
    words = cleaned.split()
    cap_words = [w for w in words if w and len(w) > 1 and w[0].isupper()]
    
    if 2 <= len(cap_words) <= 3:
        name = ' '.join(cap_words[:3])
        if (3 <= len(name) <= 50 and
            name.lower() not in ['dream group', 'pay slip', 'salary slip']):
            return name
    
    return None


def extract_amount_from_line(line):
    """Stage 4: Extract amount using multi-pattern detection"""
    # Remove currency symbols and clean
    line = re.sub(r'[₹$€£¥]', '', line)
    
    # Multiple amount patterns
    patterns = [
        r'\b(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\b',  # 90,148.00 or 90148.00
        r'\b(\d{5,}(?:\.\d{2})?)\b',  # 90148 or 90148.00
        r'\b(\d{1,3}(?:,\d{3})+)\b',  # 90,148
    ]
    
    amounts = []
    for pattern in patterns:
        matches = re.findall(pattern, line)
        for match in matches:
            try:
                amount = float(match.replace(',', ''))
                if 500 <= amount <= 10000000:
                    amounts.append(amount)
            except ValueError:
                continue
    
    # Return largest amount found (likely the main salary)
    return max(amounts) if amounts else None


def extract_company_from_line(line):
    """Extract company name from a line"""
    # Remove common keywords
    line = re.sub(r'\b(company|employer|organization|group|ltd|limited|inc|corp|payslip|pay slip)\b', '', line, flags=re.IGNORECASE)
    line = line.strip()
    
    # Pattern: Take first 1-2 capitalized words (company names are usually short)
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
            
            if len(company_words) >= 2:  # Limit to 2 words for company name
                break
        
        if company_words:
            company = ' '.join(company_words)
            if 2 <= len(company) <= 50:
                return company
    
    return None


def fallback_extract_income(lines):
    """Stage 5: Fallback heuristic - find largest monetary value"""
    all_amounts = []
    
    for line in lines:
        amounts = extract_amount_from_line(line)
        if amounts:
            all_amounts.append(amounts)
    
    # Return largest amount found
    return max(all_amounts) if all_amounts else None


def fallback_extract_employer(lines):
    """Stage 5: Fallback heuristic - scan top lines for company name"""
    # Check first 3 lines for company-like names
    for line in lines[:3]:
        # Look for lines with capitalized words before common document keywords
        if any(keyword in line.lower() for keyword in ['payslip', 'pay slip', 'salary slip']):
            # Extract text before these keywords
            parts = re.split(r'\b(payslip|pay slip|salary slip)\b', line, flags=re.IGNORECASE)
            if parts[0]:
                # Clean and extract first company-like phrase
                text = parts[0].strip()
                # Split by comma first
                segments = re.split(r',', text)
                if segments:
                    # Take first segment and extract first 2 words
                    first_segment = segments[0].strip()
                    words = first_segment.split()
                    
                    # Take first 2 capitalized words
                    company_words = []
                    for word in words[:2]:
                        if word and len(word) > 1 and (word[0].isupper() or word.isupper()):
                            company_words.append(word)
                    
                    if len(company_words) >= 2:
                        company = ' '.join(company_words)
                        if 3 <= len(company) <= 50:
                            return company
        
        # Try extracting company from line (first 2 words only)
        words = line.split()
        company_words = []
        for word in words[:2]:
            if word and len(word) > 1 and (word[0].isupper() or word.isupper()):
                company_words.append(word)
        
        if len(company_words) >= 2:
            company = ' '.join(company_words)
            if 3 <= len(company) <= 50:
                return company
    
    return None


def smart_extract_fields(text):
    """Main smart extraction engine with multi-stage parsing"""
    # Stage 1: Normalize text
    lines = normalize_text(text)
    
    if not lines:
        return {"name": None, "income": None, "employer": None, "confidence": 0.0}
    
    # Stage 2: Keyword dictionaries
    name_keywords = [
        "name", "employee name", "emp name", "worker", "staff name",
        "employee", "emp", "person"
    ]
    
    income_keywords = [
        "net pay", "net salary", "take home", "income", "earnings",
        "total earnings", "gross pay", "gross salary", "salary",
        "pay", "amount", "total pay", "basic pay", "monthly salary"
    ]
    
    employer_keywords = [
        "company", "employer", "organization", "group", "ltd",
        "limited", "corporation", "corp", "inc", "firm"
    ]
    
    # Extract fields using keyword search
    name_idx, name_line, name_conf = find_keyword_line(lines, name_keywords)
    income_idx, income_line, income_conf = find_keyword_line(lines, income_keywords)
    employer_idx, employer_line, employer_conf = find_keyword_line(lines, employer_keywords)
    
    # Stage 3: Context window extraction
    name = extract_value_from_context(lines, name_idx, "name")
    income = extract_value_from_context(lines, income_idx, "amount")
    employer = extract_value_from_context(lines, employer_idx, "company")
    
    # Stage 5: Fallback heuristics
    if not income:
        income = fallback_extract_income(lines)
    
    if not employer:
        employer = fallback_extract_employer(lines)
    
    # Stage 6: Calculate extraction confidence
    fields_attempted = 3
    fields_extracted = sum([
        1 if name else 0,
        1 if income else 0,
        1 if employer else 0
    ])
    
    confidence = fields_extracted / fields_attempted
    
    return {
        "name": name,
        "income": income,
        "employer": employer,
        "confidence": round(confidence, 2)
    }


# Legacy functions kept for backward compatibility
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
