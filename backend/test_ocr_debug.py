"""
Debug script to test OCR extraction on uploaded documents
"""

import os
import sys
from services.ocr_service import extract_text_from_image

# Test with the uploaded payslip
test_files = [
    "uploads/Employee-Payslip.png",
    "uploads/images.png",
    "uploads/4941296999.pdf",
]

print("=" * 70)
print("OCR EXTRACTION DEBUG TEST")
print("=" * 70)
print()

for file_path in test_files:
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        print()
        continue
    
    print(f"📄 Testing: {file_path}")
    print("-" * 70)
    
    try:
        result = extract_text_from_image(file_path)
        
        print(f"✓ Raw Text (first 500 chars):")
        print(f"  {result['raw_text'][:500]}")
        print()
        
        print(f"✓ Extracted Fields:")
        print(f"  Name: {result['name']}")
        print(f"  Income: {result['income']}")
        print(f"  Employer: {result['employer']}")
        print()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print()

print("=" * 70)
print("DEBUG TEST COMPLETE")
print("=" * 70)
