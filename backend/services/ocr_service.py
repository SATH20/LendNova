import pytesseract
from PIL import Image
import os
import re

def extract_text_from_image(image_path, config=None):
    """
    Extracts text from an image using Tesseract OCR.
    """
    try:
        # Check if tesseract is installed/configured
        if not os.path.exists(config.TESSERACT_CMD):
             # Fallback for development if Tesseract isn't installed
             return {
                 "raw_text": "OCR Engine Not Found - Mock Extraction",
                 "name": "John Doe (Mock)",
                 "income": 5000.0,
                 "employer": "Tech Corp (Mock)"
             }
             
        pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD
        
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        
        # Simple extraction logic (Regex based)
        extracted_data = {
            "raw_text": text,
            "name": extract_field(text, r"Name:\s*(.*)"),
            "income": extract_amount(text, r"Net Pay:\s*\$?([\d,]+\.?\d*)"),
            "employer": extract_field(text, r"Employer:\s*(.*)")
        }
        
        return extracted_data
        
    except Exception as e:
        print(f"OCR Error: {str(e)}")
        return None

def extract_field(text, pattern):
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else None

def extract_amount(text, pattern):
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        amount_str = match.group(1).replace(',', '')
        try:
            return float(amount_str)
        except ValueError:
            return None
    return None
