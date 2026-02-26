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
        "name": extract_field(text, r"Name[:\s]+([A-Za-z\s]+)"),
        "income": extract_amount(text, r"(Net Pay|Income)[:\s]*\$?([\d,]+\.?\d*)"),
        "employer": extract_field(text, r"(Employer|Company)[:\s]+([A-Za-z\s&]+)"),
    }

    return extracted_data

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
