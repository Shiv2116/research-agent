# Financial Research MVP

Minimal full-stack app for uploading a company document, extracting financial notes with DeepSeek, generating charts, and exporting a PDF report.

## Structure

```text
backend/
  app.py
  services/
    parser.py
    llm.py
    pdf_generator.py
    chart_generator.py
  uploads/
  generated/
frontend/
  src/
    App.jsx
    api.js
```

## Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export DEEPSEEK_API_KEY=your_key_here
PYTHONPATH=. .venv/bin/python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

## Notes

- Supported uploads: PDF, TXT, and CSV.
- If `DEEPSEEK_API_KEY` is missing, the backend falls back to a local heuristic extractor so the MVP still produces a report.
- Generated PDFs and charts are stored locally under `backend/generated/`.
