# Document Upload Workflow Upgrade

## Overview
Fixed the document upload workflow to align frontend with existing backend verification logic. The backend supports separate document types (payslip and bank_statement), but the frontend previously had only one upload field defaulting to "payslip".

## Changes Made

### Frontend Changes (src/app/assistant/page.tsx)

#### 1. New State Variables
- `payslipFile`: Stores selected payslip file
- `bankStatementFile`: Stores selected bank statement file
- `payslipUploaded`: Tracks if payslip has been uploaded
- `bankStatementUploaded`: Tracks if bank statement has been uploaded
- Removed: `selectedFile` (replaced by specific document states)

#### 2. New Functions

**`getDocumentRequirements()`**
- Dynamically determines required documents based on employment type
- Returns requirements object with `payslip` and `bankStatement` properties
- Each property has `required` (boolean) and `label` (string) fields

Employment Type Requirements:
- **Full-time**: Payslip (required) + Bank Statement (required)
- **Self-employed**: Bank Statement (required), Payslip (optional)
- **Part-time**: Bank Statement (required), Payslip (optional)
- **Student**: Both optional
- **Unemployed**: Both optional

**`handleFileChange(event, documentType)`**
- Updated to accept document type parameter ("payslip" or "bank_statement")
- Stores files in separate state variables based on type
- Validates file types (PNG, JPG, PDF)

**`handleVerify()`**
- Completely rewritten to handle multiple documents
- Validates required documents based on employment type
- Uploads payslip first (if available and not uploaded)
- Then uploads bank statement (if available and not uploaded)
- Each upload sends correct `document_type` to backend
- Updates verification status after each upload
- Provides detailed feedback via feed messages

#### 3. UI Changes

**Input Form (mode === "input")**
- Replaced single "Optional Document Upload" field
- Added "Document Requirements" section
- Dynamically displays required/optional documents based on employment type
- Each document has:
  - Label with Required/Optional badge
  - File selection button
  - Visual confirmation when file is selected
  - Proper styling and hover effects

**Results Page (mode === "results")**
- Added "Complete Verification" section when verification is incomplete
- Shows verification checklist with status indicators:
  - ✔ for uploaded documents
  - ○ for pending documents
- Displays separate upload fields for missing documents
- Shows dynamic status message based on verification result:
  - **VERIFIED/COMPLETED**: "✓ All required documents uploaded. Verification complete." (green)
  - **PARTIAL**: "⚠ Documents uploaded. Financial mismatch detected. Additional review required." (purple)
  - **INCOMPLETE**: "⚠ Documents uploaded. Required documents missing. Upload additional documents." (red)
  - **PENDING**: "✓ All required documents uploaded. Processing verification..." (green)
- Upload button disabled until at least one document is selected

## Backend Integration

The changes maintain full compatibility with existing backend:
- `/api/ocr-extract` endpoint receives correct `document_type` parameter
- `verification_engine.py` routes verification based on employment type
- `bank_statement_parser.py` processes bank statements correctly
- No backend modifications required

## User Experience Flow

### For Full-time Employees:
1. Fill in assessment form
2. See both Payslip (Required) and Bank Statement (Required)
3. Upload both documents
4. Run assessment → Preliminary results
5. Upload documents → Full verification
6. Status changes: PRELIMINARY → VERIFIED

### For Self-employed:
1. Fill in assessment form
2. See Bank Statement (Required), Payslip (Optional)
3. Upload bank statement (minimum requirement)
4. Run assessment → Preliminary results
5. Upload bank statement → Verification based on bank data
6. Status changes: PRELIMINARY → VERIFIED

### For Students/Unemployed:
1. Fill in assessment form
2. See both documents marked as Optional
3. Can run assessment without documents
4. Can optionally upload documents for enhanced verification

## Benefits

1. **Clear Requirements**: Users know exactly what documents are needed
2. **Flexible Upload**: Can upload documents separately or together
3. **Progress Tracking**: Visual checklist shows verification status
4. **Employment-Aware**: Requirements adapt to employment type
5. **Backend Aligned**: Correctly sends document_type to backend
6. **No Breaking Changes**: Existing backend logic unchanged
