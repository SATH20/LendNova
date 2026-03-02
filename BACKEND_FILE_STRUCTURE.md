# Backend File Structure - Complete Overview

## Root Level Files

### 1. **app.py** - Application Entry Point
**Purpose**: Main Flask application factory and server initialization
- Creates Flask app with configuration
- Initializes database (SQLAlchemy) and serialization (Marshmallow)
- Enables CORS for frontend communication
- Registers all API blueprints (routes)
- Sets up error handlers (404, 500)
- Auto-creates database tables on startup
- Auto-trains ML models if not present
- Includes schema migration logic for assessments table

**Key Functions**:
- `create_app()`: Factory pattern for app creation
- `_ensure_assessments_schema()`: Database migration for new columns

### 2. **config.py** - Configuration Management
**Purpose**: Centralized configuration for the application
- Loads environment variables from `.env` file
- Defines database connection string
- Sets paths for ML model artifacts
- Configures file upload settings
- Sets Tesseract OCR path

**Configuration Items**:
- `SECRET_KEY`: Flask secret for sessions
- `SQLALCHEMY_DATABASE_URI`: Database connection
- `MODEL_PATH`: Trained ML model location
- `PIPELINE_PATH`: Preprocessing pipeline location
- `FEATURE_STATS_PATH`: Feature statistics location
- `UPLOAD_FOLDER`: Document upload directory
- `ALLOWED_EXTENSIONS`: Valid file types (png, jpg, jpeg, pdf)
- `TESSERACT_CMD`: Tesseract OCR executable path

### 3. **requirements.txt** - Python Dependencies
**Purpose**: Lists all required Python packages
- Flask ecosystem (flask, flask-cors, flask-sqlalchemy, flask-marshmallow)
- Database (sqlalchemy, psycopg2-binary, marshmallow-sqlalchemy)
- ML/Data Science (scikit-learn, pandas, numpy, joblib)
- OCR (pytesseract, pdf2image, PyPDF2, Pillow)
- Utilities (python-dotenv)

### 4. **README.md** - Documentation
**Purpose**: Setup instructions and API documentation
- Installation steps
- Tesseract OCR setup guide
- API endpoint documentation
- Project structure overview

### 5. **test_verification.py** & **test_verification_standalone.py**
**Purpose**: Test scripts for verification engine
- Test different employment types
- Validate document verification logic
- Check payslip and bank statement processing

---

## Database Folder (`backend/database/`)

### 1. **db.py** - Database Initialization
**Purpose**: Creates SQLAlchemy and Marshmallow instances
- `db`: SQLAlchemy database instance
- `ma`: Marshmallow serialization instance

### 2. **models.py** - Database Models
**Purpose**: Defines database schema using SQLAlchemy ORM

**Assessment Model**:
- Stores credit assessment records
- Fields:
  - Input: income, expenses, employment_type, job_tenure
  - Declared vs Verified: declared_income, verified_income, declared_expense, verified_expense
  - Prediction: credit_score, approval_probability, risk_band, model_used, confidence_score
  - Verification: assessment_status, verification_status, trust_score, identity_status
  - Flags: fraud_probability, verification_reasons, verification_flags
  - Stability: income_stability_score, expense_pattern_score
  - Metadata: timestamp, verification_method, identity_hash

**Document Model**:
- Stores uploaded documents
- Fields:
  - assessment_id (foreign key)
  - document_type (payslip, bank_statement, etc.)
  - extracted_text (masked OCR output)
  - fraud_flags (JSON string)
  - upload_time

### 3. **schemas.py** - Data Validation & Serialization
**Purpose**: Marshmallow schemas for request/response validation

**Schemas**:
- `AssessmentInputSchema`: Validates incoming assessment requests
- `AssessmentOutputSchema`: Serializes assessment responses
- `OcrResultSchema`: Validates OCR extraction results
- `FraudCheckInputSchema`: Validates fraud check requests

---

## Routes Folder (`backend/routes/`)

### 1. **predict.py** - Credit Scoring Endpoint
**Purpose**: `/api/predict` - Main credit assessment endpoint
- Accepts: income, expenses, employment_type, job_tenure
- Loads trained ML model and preprocessor
- Transforms input features
- Predicts approval probability
- Calculates credit score (300-900 range)
- Determines risk band (Low/Medium/High)
- Generates explainability factors
- Saves assessment to database
- Returns: credit_score, approval_probability, risk_band, top_factors, etc.

### 2. **ocr.py** - Document Upload & Verification
**Purpose**: `/api/ocr-extract` - Document upload and OCR processing
- Accepts file uploads (PNG, JPG, PDF)
- Validates file type
- Saves file to uploads folder
- Extracts text using OCR service
- Runs identity verification (if structured data found)
- Runs underwriting verification (payslip vs bank statement)
- Updates assessment with verification results
- Returns: extracted data, verification status, fraud flags

**Key Logic**:
- Distinguishes between payslip and bank_statement via `document_type` parameter
- Routes to appropriate verification engine based on document type
- Updates assessment status: PRELIMINARY → PARTIAL → VERIFIED

### 3. **fraud.py** - Fraud Detection Endpoint
**Purpose**: `/api/fraud-check` - Standalone fraud analysis
- Compares form data vs OCR data
- Runs identity verification checks
- Updates assessment with fraud probability
- Returns: fraud_probability, trust_score, identity_status, verification_reasons

### 4. **assessments.py** - History Endpoint
**Purpose**: `/api/assessments` - Retrieves assessment history
- Supports pagination (page, per_page parameters)
- Returns list of past assessments
- Ordered by timestamp (newest first)

---

## Services Folder (`backend/services/`)

### 1. **ocr_service.py** - OCR Text Extraction
**Purpose**: Extracts text and structured data from documents
- Handles images (PNG, JPG) and PDFs
- Uses Tesseract OCR for text extraction
- Parses structured fields: name, income, employer
- Uses regex patterns to find financial data
- Returns: raw_text, name, income, employer

**Key Functions**:
- `extract_text_from_image()`: Main OCR function
- `_extract_from_pdf()`: PDF-specific extraction
- `_extract_from_image()`: Image-specific extraction
- `_parse_structured_data()`: Extracts name, income, employer

### 2. **identity_verification.py** - Identity & Fraud Checks
**Purpose**: Verifies identity consistency and detects fraud
- Compares declared vs extracted data
- Checks name, income, employer consistency
- Validates document authenticity (PDF metadata)
- Assesses OCR confidence
- Evaluates data plausibility
- Tracks behavioral patterns (repeat submissions)
- Calculates trust score (0-1)
- Determines identity status (VERIFIED/SUSPICIOUS/FAILED)

**Verification Components**:
- Name matching (SequenceMatcher similarity)
- Income consistency (tolerance: 12%)
- Employer matching
- PDF authenticity (checks for editing software in metadata)
- OCR confidence (based on extracted fields)
- Plausibility checks (income vs tenure, employment type logic)
- Behavioral analysis (repeat submissions tracking)

### 3. **verification_engine.py** - Employment-Based Verification Router
**Purpose**: Routes verification based on employment type
- Determines required documents per employment type
- Validates financial data from payslips and bank statements
- Calculates trust scores
- Returns verification status

**Employment Type Logic**:
- **Full-time (Salaried)**: Requires payslip + bank statement
  - Payslip verifies income
  - Bank statement verifies expenses
- **Self-employed**: Requires bank statement only
  - Estimates income from bank credits
  - More lenient mismatch tolerance (30%)
- **Part-time**: Requires bank statement
  - Analyzes income volatility
- **Student**: Optional documents
  - Reduced income verification requirements
- **Unemployed**: Optional documents
  - Focus on expense validation

**Key Functions**:
- `verification_router()`: Main routing function
- `verify_salaried()`: Full-time verification
- `verify_self_employed()`: Self-employed verification
- `verify_student()`: Student verification
- `verify_part_time()`: Part-time verification
- `verify_unemployed()`: Unemployed verification
- `calculate_trust_score()`: Weighted trust calculation
- `get_final_values()`: Returns verified or declared values

### 4. **verification_engine_temp.py**
**Purpose**: Backup/alternative version of verification engine (likely for testing)

### 5. **bank_statement_parser.py** - Bank Statement Analysis
**Purpose**: Parses bank statements to extract financial metrics
- Extracts transactions (credits and debits)
- Calculates monthly averages
- Detects recurring payments
- Computes income stability score
- Computes expense pattern score

**Key Functions**:
- `parse_bank_statement()`: Main parsing function
- `extract_transactions()`: Finds transaction amounts
- `estimate_months_covered()`: Determines statement period
- `detect_recurring_payments()`: Finds recurring expenses
- `calculate_income_stability()`: Coefficient of variation analysis
- `calculate_expense_pattern()`: Regularity scoring

**Returns**:
- total_credits, total_debits
- monthly_avg_credits, monthly_avg_debits
- recurring_payments (list)
- income_stability_score (0-1)
- expense_pattern_score (0-1)
- transaction_count, months_covered

### 6. **fraud_engine.py** - Anomaly Detection
**Purpose**: Detects fraudulent patterns using ML
- Uses IsolationForest for anomaly detection
- Checks income/expense mismatches
- Validates document expiry dates
- Detects suspicious formatting
- Calculates fraud probability

**Key Functions**:
- `detect_fraud()`: Main fraud detection
- `_get_isolation_model()`: Lazy-loads IsolationForest model

**Fraud Flags**:
- Income mismatch beyond tolerance
- Incomplete name extraction
- Expired documents
- Suspicious formatting

### 7. **explainability.py** - Model Interpretability
**Purpose**: Explains ML model decisions
- Extracts feature importances from model
- Calculates impact of each feature
- Returns top positive/negative factors
- Supports both linear (coef_) and tree-based (feature_importances_) models

**Key Function**:
- `explain_decision()`: Returns top N factors with impact scores

---

## ML Folder (`backend/ml/`)

### 1. **train.py** - Model Training Pipeline
**Purpose**: Trains and selects best ML model
- Generates synthetic training data (2400 samples)
- Tests 3 models: Logistic Regression, Random Forest, Gradient Boosting
- Uses 5-fold cross-validation
- Selects best model based on ROC-AUC
- Saves model, preprocessor, and feature statistics

**Key Functions**:
- `generate_synthetic_data()`: Creates training dataset
- `build_preprocessor()`: Creates feature engineering pipeline
- `evaluate_pipeline()`: Calculates metrics
- `train_models()`: Main training orchestrator

**Synthetic Data Generation**:
- Income: Log-normal distribution (mean=8.5, sigma=0.8)
- Expenses: 30-90% of income
- Tenure: Exponential distribution (scale=3.0)
- Employment types: Full-time (60%), Part-time (15%), Self-employed (15%), Unemployed (5%), Student (5%)
- Target: Risk score based on expense ratio, tenure, employment type

### 2. **feature_engineering.py** - Feature Transformation
**Purpose**: Custom transformer for feature engineering
- Converts raw inputs to ML-ready features
- Creates derived features

**Engineered Features**:
- `savings_ratio`: (income - expenses) / income
- `expense_to_income_ratio`: expenses / income
- `tenure_years`: job_tenure (renamed)
- `stability_score`: log(tenure) * 10

### 3. **evaluate.py** - Model Evaluation
**Purpose**: Tests trained model on fresh data
- Generates test dataset (800 samples)
- Loads saved model and preprocessor
- Calculates performance metrics
- Returns: ROC-AUC, F1, Precision, Recall

---

## Models Folder (`backend/models/`)

### 1. **ml_model.pkl** - Trained ML Model
**Purpose**: Serialized scikit-learn model (Logistic Regression, Random Forest, or Gradient Boosting)

### 2. **preprocess_pipeline.pkl** - Feature Preprocessing Pipeline
**Purpose**: Serialized preprocessing pipeline
- Feature engineering
- Numeric scaling (StandardScaler)
- Categorical encoding (OneHotEncoder)

### 3. **feature_stats.pkl** - Feature Metadata
**Purpose**: Stores feature names, means, and model type
- Used for explainability calculations
- Contains feature_names, feature_means, model name

---

## Utils Folder (`backend/utils/`)

### 1. **helpers.py** - Utility Functions
**Purpose**: Common helper functions

**Functions**:
- `mask_amount()`: Rounds amounts to nearest bucket (privacy)
- `mask_text()`: Replaces digits with 'X' (privacy)
- `clean_text()`: Normalizes whitespace
- `credit_score_from_prob()`: Converts probability to 300-900 score
- `risk_band_from_score()`: Maps score to Low/Medium/High
- `confidence_from_prob()`: Calculates model confidence
- `parse_date()`: Extracts dates from text (multiple formats)

---

## Instance Folder (`backend/instance/`)

### 1. **lendnova.db** - SQLite Database
**Purpose**: Local database file (development)
- Stores assessments and documents tables
- Auto-created on first run

---

## Uploads Folder (`backend/uploads/`)

**Purpose**: Stores uploaded documents
- Contains sample payslips and bank statements
- Files: 4941296999.pdf, Employee-Payslip.png, images.png, standard_salary_slip_format.png, statement.png

---

## Summary

### Data Flow:
1. **Assessment Request** → predict.py → ML model → Database
2. **Document Upload** → ocr.py → OCR service → Identity verification → Verification engine → Database
3. **Fraud Check** → fraud.py → Identity verification → Database
4. **History Request** → assessments.py → Database

### Key Integrations:
- **Frontend** ↔ **Routes** (API endpoints)
- **Routes** ↔ **Services** (business logic)
- **Services** ↔ **Database** (data persistence)
- **ML** ↔ **Routes** (model inference)

### Verification Pipeline:
1. User uploads document (payslip or bank statement)
2. OCR extracts text and structured data
3. Identity verification checks consistency
4. Verification engine routes based on employment type
5. Bank statement parser analyzes transactions (if applicable)
6. Trust score calculated
7. Assessment status updated (PRELIMINARY → PARTIAL → VERIFIED)
