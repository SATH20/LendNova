# LENDNOVA Backend

Production-ready backend for the LENDNOVA AI Creditworthiness Prediction System.

## Features
- **Credit Scoring**: Machine learning pipeline (Gradient Boosting) to predict approval probability.
- **Fraud Detection**: Cross-reference user data with OCR extractions and anomaly detection rules.
- **OCR Service**: Extract fields from payslips/IDs using Tesseract.
- **Explainability**: Provide top impacting factors for each decision.
- **History**: Store and retrieve assessment logs via PostgreSQL/SQLite.

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

5. **Configuration**
   Copy `.env.example` to `.env` and update values.
   ```bash
   cp .env.example .env
   ```

6. **Run Server**
   ```bash
   python app.py
   ```
   The server will start at `http://localhost:5000`.
   On first run, it will automatically generate synthetic data and train the initial ML model.

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

### 3. Fraud Check
**POST** `/api/fraud-check`
```json
{
  "form_data": { ... },
  "ocr_data": { "income": 4800, "name": "John Doe", ... }
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
