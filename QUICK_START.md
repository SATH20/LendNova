# LendNova Identity Verification - Quick Start Guide

## 🚀 Getting Started

### Prerequisites
- Python 3.8+ with Flask
- Node.js 18+ with Next.js
- All dependencies installed

### Start the System

#### 1. Start Backend (Terminal 1)
```bash
cd backend
python app.py
```
Backend runs on: http://localhost:5000

#### 2. Start Frontend (Terminal 2)
```bash
npm run dev
```
Frontend runs on: http://localhost:3000

## 📋 Using the Identity Verification System

### Step 1: Navigate to Assessment Page
Open http://localhost:3000/assistant

### Step 2: Enter User Information
**Required Fields:**
- Monthly Income (e.g., 4200)
- Monthly Expenses (e.g., 1700)
- Employment Type (Full-time, Part-time, etc.)
- Job Tenure in Years (e.g., 3)

**Optional Identity Fields (for verification):**
- Full Name (e.g., "John Smith")
- Employer (e.g., "Tech Corp")
- Mobile (e.g., "+1234567890")

### Step 3: Run Preliminary Assessment
Click "Run Assessment" button
- System generates credit score
- Shows approval probability
- Status: "Preliminary Assessment"

### Step 4: Upload Document for Verification
After preliminary assessment:
1. Click "Upload documents to verify" button
2. Select a document (PNG, JPG, or PDF)
3. System performs:
   - OCR extraction
   - Identity verification
   - Trust score calculation
   - Fraud analysis

### Step 5: View Verification Results
Navigate to "Fraud Analysis" tab to see:
- **Identity Verification Card**
  - Trust Score (0-100%)
  - Identity Status (Verified/Suspicious/Failed)
  - Verification Pipeline (5 stages)
  - Detailed findings
- **Fraud Analysis**
  - Fraud probability
  - OCR extracted data
- **Why Risk Increased**
  - Detailed explanations for each flag

## 🎯 Understanding Results

### Trust Score Ranges
- **75-100%**: ✅ VERIFIED - Identity checks passed
- **50-74%**: ⚠️ SUSPICIOUS - Manual review recommended
- **0-49%**: ❌ FAILED - Verification issues detected

### Common Verification Flags
- **Income mismatch detected**: User input doesn't match document
- **Name mismatch detected**: Name inconsistency found
- **OCR confidence low**: Document quality issues
- **Rounded income pattern**: Suspiciously round numbers
- **Student income unusually high**: Implausible for employment type
- **Rapid repeat submissions**: Behavioral fraud indicator

## 🧪 Test Scenarios

### Scenario 1: Legitimate User
```
Income: 4500
Expenses: 1800
Employment: Full-time
Tenure: 3.5
Name: John Smith
Employer: Tech Corp
Document: Genuine payslip
Expected: VERIFIED (>75% trust score)
```

### Scenario 2: Income Mismatch
```
Income: 5000 (user input)
Document shows: 3500
Expected: SUSPICIOUS/FAILED + "Income mismatch detected"
```

### Scenario 3: Implausible Data
```
Income: 8000
Employment: Student
Expected: SUSPICIOUS + "Student income unusually high"
```

### Scenario 4: Rounded Income
```
Income: 50000 (exactly)
Expected: Flag "Rounded income pattern detected"
```

### Scenario 5: Name Mismatch
```
Name: Michael Johnson (user input)
Document shows: Mike Jones
Expected: Flag "Name mismatch detected"
```

## 📊 Verification Pipeline Stages

1. **User Data** ✓
   - Consent-driven input collection

2. **OCR Extraction** ✓
   - Document text extraction
   - Field identification

3. **Identity Check** ✓
   - Name matching (30% weight)
   - Income validation
   - Employer verification

4. **Fraud Analysis** ✓
   - Document authenticity (15% weight)
   - Data plausibility (25% weight)
   - Behavioral risk (10% weight)
   - OCR confidence (20% weight)

5. **Decision** ✓
   - Trust score calculation
   - Status determination
   - Fraud probability

## 🔍 Troubleshooting

### Issue: "Upload a document to verify" error
**Solution**: Select a file before clicking verify button

### Issue: Fraud Analysis tab not visible
**Solution**: Complete document verification first

### Issue: Low trust score on legitimate data
**Possible causes:**
- Document quality issues (low OCR confidence)
- Minor data entry differences
- Rounded income amounts
- Short employment tenure with high income

### Issue: Backend connection error
**Solution**: Ensure Flask server is running on port 5000

## 📁 Key Files

### Backend
- `backend/services/identity_verification.py` - Verification logic
- `backend/routes/ocr.py` - OCR and verification endpoint
- `backend/database/models.py` - Database schema

### Frontend
- `src/app/assistant/page.tsx` - Main assessment page
- `src/components/IdentityVerificationCard.tsx` - Verification display
- `src/lib/api.ts` - API client

## 🎨 UI Features

### Assessment Summary
- Credit Score display
- Approval Probability meter
- Risk Band indicator
- Trust Score (after verification)
- Fraud Probability (after verification)

### Fraud Analysis Tab
- Identity Verification Card
- Trust Score meter with color coding
- Verification pipeline visualization
- Detailed findings with badges
- "Why Risk Increased" explanations

### Visual Indicators
- 🟢 Green: Verified/Low Risk
- 🟡 Yellow: Suspicious/Medium Risk
- 🔴 Red: Failed/High Risk

## 💡 Tips

1. **For Best Results**: Enter accurate identity information matching your document
2. **Document Quality**: Use clear, high-resolution images or PDFs
3. **Avoid Editing**: Don't use Canva/Photoshop for documents (will be flagged)
4. **Be Consistent**: Ensure name, income, employer match across inputs
5. **Realistic Data**: Avoid suspiciously round numbers

## 📞 Support

For issues or questions:
1. Check `IDENTITY_VERIFICATION_UPGRADE.md` for detailed documentation
2. Review `UPGRADE_SUMMARY.md` for implementation details
3. Run `backend/test_verification_standalone.py` to test verification logic

## ✅ Quick Checklist

Before testing:
- [ ] Backend server running (port 5000)
- [ ] Frontend server running (port 3000)
- [ ] Test document ready (PNG/JPG/PDF)
- [ ] User information prepared

During testing:
- [ ] Enter all required fields
- [ ] Add optional identity fields
- [ ] Run preliminary assessment
- [ ] Upload document
- [ ] Check Fraud Analysis tab
- [ ] Review verification results

## 🎯 Success Indicators

You'll know the system is working when:
- ✅ Preliminary assessment generates credit score
- ✅ Document upload triggers verification
- ✅ Fraud Analysis tab becomes available
- ✅ Trust score displays (0-100%)
- ✅ Identity status shows (Verified/Suspicious/Failed)
- ✅ Verification reasons list appears
- ✅ "Why Risk Increased" section explains flags

---

**Ready to test?** Start both servers and navigate to http://localhost:3000/assistant!
