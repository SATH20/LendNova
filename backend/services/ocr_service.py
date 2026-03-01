import os
import re
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from utils.helpers import clean_text

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

    extracted_data = {
        "raw_text": text,
        "name": extract_name(text),
        "income": extract_income(text),
        "employer": extract_employer(text),
    }

    return extracted_data

def extract_name(text):
    """Extract name from document with multiple pattern matching"""
    patterns = [
        r"Name\s+([A-Z][a-z]+\s+[A-Z][a-z]+)(?:\s|$)",  # "Name John Doe"
        r"sno\s+Name\s+([A-Z][a-z]+\s+[A-Z][a-z]+)",  # "sno Name John Doe"
        r"Employee\s+Name[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)",
        r"(?:Employee|Name)[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            name = match.group(1).strip()
            # Filter out common non-name words and limit to 2-3 words
            words = name.split()
            if (len(name) > 2 and len(name) < 50 and 
                len(words) <= 3 and
                name.lower() not in ['dream group', 'company', 'organization']):
                return name
    return None

def extract_income(text):
    """Extract income/salary from document with multiple pattern matching"""
    # First, try to find amounts that look like salaries (5+ digits)
    salary_candidates = []
    
    patterns = [
        r"(?:Net\s+)?Pay\s*\(?[Rr]ounded\)?\s*([0-9,]+\.?\d*)",  # "Net Pay (Rounded) 90,148.00"
        r"(?:Basic|Base)\s+Pay[:\s]*([0-9,]+\.?\d*)",
        r"(?:Net\s+)?Pay[:\s]*([0-9,]+\.?\d*)",
        r"(?:Gross|Total)\s+(?:Pay|Salary|Earnings)[:\s]*([0-9,]+\.?\d*)",
        r"(?:Monthly|Annual)\s+(?:Income|Salary)[:\s]*([0-9,]+\.?\d*)",
        r"(?:Salary|Income)[:\s]*([0-9,]+\.?\d*)",
        r"Pay\s+([0-9,]+\.?\d*)",  # Simple "Pay XXXXX" format
        r"Total\s+Earnings\s+([0-9,]+\.?\d*)",  # "Total Earnings 92,148.00"
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            amount_str = match.group(1).replace(",", "").strip()
            try:
                amount = float(amount_str)
                # Validate reasonable income range (500 - 10,000,000)
                if 500 <= amount <= 10000000:
                    salary_candidates.append(amount)
            except ValueError:
                continue
    
    # Return the first valid salary found (prefer Net Pay over others)
    if salary_candidates:
        return salary_candidates[0]
    
    # Fallback: look for large numbers that might be salary
    large_numbers = re.findall(r'\b([0-9]{5,}(?:,[0-9]{3})*(?:\.[0-9]{2})?)\b', text)
    for num_str in large_numbers:
        try:
            amount = float(num_str.replace(",", ""))
            if 500 <= amount <= 10000000:
                return amount
        except ValueError:
            continue
    
    return None

def extract_employer(text):
    """Extract employer/company name from document with multiple pattern matching"""
    patterns = [
        r"^([A-Za-z0-9\s\&\-\.]+?)\s+(?:Payslip|Pay\s+Slip)",  # Company name before "Payslip"
        r"^([A-Za-z0-9\s\&\-\.]+?)\s+(?:PAV|Baling|Ist\s+Flor)",  # Company at start of document
        r"(?:Employer|Company|Organization)[:\s]+([A-Za-z0-9\s\&\-\.]+?)(?:\n|$)",
        r"(?:Employer|Company)[:\s]+([A-Za-z0-9\s\&\-\.]+?)(?:\s{2,}|$)",
        r"(?:Employed\s+by|Works\s+at)[:\s]+([A-Za-z0-9\s\&\-\.]+?)(?:\n|$)",
        r"(?:Department|Dept)[:\s]+([A-Za-z0-9\s\&\-\.]+?)(?:\n|$)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            employer = match.group(1).strip()
            # Clean up employer name - remove extra spaces and limit length
            employer = ' '.join(employer.split())
            if len(employer) > 1 and len(employer) < 100:
                return employer
    return None

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
