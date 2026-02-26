# LENDNOVA Backend

Production-ready backend for the LENDNOVA AI Creditworthiness Prediction System.

## Features
- **Credit Scoring**: ML pipeline with Logistic Regression, Random Forest, and Gradient Boosting selection.
- **Fraud Detection**: Rule-based checks with IsolationForest anomaly scoring.
- **OCR Service**: Extracts Name, Income, and Employer from images or PDFs.
- **Explainability**: Returns top positive and negative impacts per prediction.
- **History**: Stores and retrieves assessment logs via PostgreSQL/SQLite.

## Setup

1. **Install Python 3.10+**

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Tesseract OCR**
   - **Windows**: Download installer from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki).
     - Add installation path to System PATH or update `.env`.
   - **Linux**: `sudo apt-get install tesseract-ocr`
   - **Mac**: `brew install tesseract`

5. **Install PDF OCR Dependencies (Optional)**
   - **Windows**: Install Poppler and add to PATH for `pdf2image`.
   - **Linux**: `sudo apt-get install poppler-utils`
   - **Mac**: `brew install poppler`

6. **Configuration**
   Copy `.env.example` to `.env` and update values.
   ```bash
   cp .env.example .env
   ```

7. **Run Server**
   ```bash
   python app.py
   ```
   The server will start at `http://localhost:5000`.
   On first run, it will automatically generate synthetic data and train the initial ML model.

8. **Optional: Retrain or Evaluate**
   ```bash
   python ml/train.py
   python ml/evaluate.py
   ```

## API Endpoints

### 1. Predict Credit Score
**POST** `/api/predict`
```json
{
  "income": 5000,
  "expenses": 2000,
  "employment_type": "Full-time",
  "job_tenure": 3.5
}
```

### 2. OCR Extraction
**POST** `/api/ocr-extract`
- Body: `form-data`
- Key: `file` (Image/PDF)
- Optional: `document_type`, `assessment_id`

### 3. Fraud Check
**POST** `/api/fraud-check`
```json
{
  "form_data": {
    "income": 5000,
    "expenses": 1800,
    "employment_type": "Full-time",
    "job_tenure": 4
  },
  "ocr_data": {
    "income": 4800,
    "name": "John Doe",
    "employer": "Northwind Labs",
    "extracted_text": "Name: John Doe Income: 4800 Employer: Northwind Labs"
  }
}
```

### 4. Assessment History
**GET** `/api/assessments?page=1&per_page=10`

## Project Structure
- `app.py`: Application entry point.
- `routes/`: API controllers.
- `services/`: Business logic (Fraud, OCR, Explainability).
- `ml/`: Model training and feature engineering.
- `database/`: Models and schemas.
- `models/`: Persisted model artifacts.
