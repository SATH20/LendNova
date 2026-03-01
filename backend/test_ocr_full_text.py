"""
Debug script to see full OCR text
"""

import os
from services.ocr_service import extract_text_from_image

file_path = "uploads/Employee-Payslip.png"

if os.path.exists(file_path):
    result = extract_text_from_image(file_path)
    print("FULL RAW TEXT:")
    print("=" * 70)
    print(result['raw_text'])
    print("=" * 70)
else:
    print(f"File not found: {file_path}")
