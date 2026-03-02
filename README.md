# LendNova

An AI credit assessment platform that actually explains its decisions.

## What's this about?

Ever applied for a loan and got rejected with zero explanation? Yeah, that sucks. LendNova is my attempt at fixing that. It's a credit scoring system that uses machine learning to evaluate loan applications, but here's the kicker - it tells you exactly why it made each decision.

I built this because traditional credit scoring feels like a black box. You throw your data in, and some mysterious algorithm spits out a number. Not cool. With LendNova, you get to see which factors helped your score and which ones hurt it.

## What it does

- Analyzes your income, expenses, and employment info
- Reads documents like payslips and bank statements (OCR magic)
- Checks for fraud patterns
- Gives you a credit score with actual reasoning
- Shows you the top 3 things working for you and the top 3 things working against you

The whole thing runs in about 2 seconds, which is pretty neat.

## Tech stuff

**Frontend:** Next.js, React, TypeScript, Tailwind  
**Backend:** Flask, Python  
**ML:** scikit-learn, SHAP for explainability  
**OCR:** Tesseract  
**Database:** SQLite (easy to swap for Postgres)

Nothing too fancy, just solid tools that work.

## Getting it running

You'll need Python 3.11+ and Node.js 20+. Also install Tesseract if you want the document scanning to work.

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python app.py
```

**Frontend:**
```bash
npm install
npm run dev
```

Backend runs on port 5000, frontend on 3000. Open localhost:3000 and you're good to go.

## How to use it

The main endpoint is `/api/analyze`. Send it some data:

```bash
curl -X POST http://localhost:5000/api/analyze \
  -F "income=5000" \
  -F "expenses=2000" \
  -F "employment_type=Full-time" \
  -F "job_tenure=3.5"
```

You'll get back something like:

```json
{
  "credit_score": 720,
  "risk_band": "Low",
  "decision": "APPROVED",
  "explainability": {
    "positive_factors": [
      {"feature": "High income", "impact": 0.35},
      {"feature": "Stable employment", "impact": 0.28}
    ],
    "risk_factors": []
  }
}
```

Pretty straightforward.

## How it actually works

Here's the flow when you submit an application:

```
Your Application
      |
      v
┌─────────────────┐
│  OCR Extraction │  → Reads your payslip/bank statement
└────────┬────────┘
         |
         v
┌─────────────────┐
│  Verification   │  → Checks if your docs match what you said
└────────┬────────┘
         |
         v
┌─────────────────┐
│ Fraud Detection │  → Looks for suspicious patterns
└────────┬────────┘
         |
         v
┌─────────────────┐
│  ML Prediction  │  → Initial probability from trained model
└────────┬────────┘
         |
         v
┌─────────────────┐
│ Decision Engine │  → Applies rules, calculates final score
└────────┬────────┘
         |
         v
┌─────────────────┐
│  Explainability │  → SHAP tells you why
└────────┬────────┘
         |
         v
    Your Result
```

Different employment types get different treatment. If you're salaried, we expect a payslip. Self-employed? Just the bank statement is fine. Students get more lenient requirements.

## Architecture

The system has three main parts:

```
┌──────────────────────────────────────────────────┐
│                   Frontend                       │
│  Next.js dashboard where you interact with it    │
└─────────────────┬────────────────────────────────┘
                  |
                  | HTTP requests
                  v
┌──────────────────────────────────────────────────┐
│                Flask Backend                     │
│                                                  │
│  /api/analyze  ←  main endpoint                  │
│  /api/predict  ←  just ML scoring                │
│  /api/fraud    ←  just fraud check               │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │   OCR    │  │ Verifier │  │  Fraud   │      │
│  │ Service  │  │  Engine  │  │  Engine  │      │
│  └──────────┘  └──────────┘  └──────────┘      │
│                                                  │
│  ┌──────────┐  ┌──────────┐                     │
│  │    ML    │  │   SHAP   │                     │
│  │  Model   │  │Explainer │                     │
│  └──────────┘  └──────────┘                     │
└─────────────────┬────────────────────────────────┘
                  |
                  v
┌──────────────────────────────────────────────────┐
│              SQLite Database                     │
│  Stores assessments, documents, history          │
└──────────────────────────────────────────────────┘
```

Everything's modular. Each service does one thing and does it well. The decision orchestrator ties it all together.

## Project structure

```
backend/
  routes/analyze.py          # main API endpoint
  services/
    verification_engine.py   # handles different employment types
    fraud_engine.py          # anomaly detection
    decision_orchestrator.py # final scoring logic
  explainability/
    shap_explainer.py        # makes decisions interpretable
  ml/
    train.py                 # model training script

src/
  app/page.tsx               # main dashboard
  components/                # UI components
```

## Testing

```bash
cd backend
python test_analyze_simple.py
```

Should see all tests pass. If not, something's broken.

## Things to know

- The ML model is trained on synthetic data (for now)
- OCR works best with clear, high-res scans
- All sensitive data gets masked before storage
- The system is deterministic - same input always gives same output

## Stuff I want to add

- Support for more document types
- Better mobile experience
- Multi-language support
- Integration with actual credit bureaus
- Real-time model updates

## Why I built this

Started as a university project, turned into something I actually think could be useful. The financial industry needs more transparency, especially in lending. If this helps even a few people understand why they got rejected (and what to fix), that's a win.

## Contributing

Found a bug? Have an idea? Open an issue or send a PR. I'm pretty responsive.

## License

MIT - do whatever you want with it.

---

Built by someone who thinks credit scoring should be less mysterious.

If this helped you, star it. If it didn't, tell me why.
