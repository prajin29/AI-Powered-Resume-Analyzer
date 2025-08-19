# AI-Powered Resume Analyzer (Streamlit)

An interactive Streamlit app that analyzes resumes using the Cohere API (default). You can also adapt it to OpenAI if desired. Upload a PDF/DOCX/TXT resume, optionally paste a job description, and get structured insights, a fit score, and improvement suggestions.

## Prerequisites
- Python 3.9+
- A Cohere API key (recommended) or an OpenAI API key

## Setup

```bash
python -m venv .venv
. .venv/Scripts/Activate  # Windows PowerShell
pip install -r requirements.txt
```

Set your API key by one of the following methods:
- Cohere via environment variable (recommended)
  - PowerShell: `$env:COHERE_API_KEY = "your-cohere-key"`
- Cohere via Streamlit secrets:
  - Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and set `COHERE_API_KEY = "your-cohere-key"`
- Or paste the key into the app sidebar at runtime (hidden if server key is set)

## Run locally

```bash
streamlit run app.py
```

## Deploy

### Streamlit Community Cloud (fastest)
1. Push this project to a GitHub repo.
2. Go to the Streamlit Cloud dashboard → New app → pick your repo/branch, `app.py` as the app file.
3. In App settings → Secrets, add:
```
COHERE_API_KEY = "your-cohere-key"
```
4. Deploy. The sidebar key field will be hidden since the server has a key.

### Any server / VM
- Set the environment variable and run the app on the server:
```bash
export COHERE_API_KEY="your-cohere-key"  # PowerShell: $env:COHERE_API_KEY = '...'
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```
- Put a reverse proxy (optional) in front and add HTTPS.

## Features
- Upload resume as PDF, DOCX, or TXT
- Extracts text locally from files (no upload of raw files to the API)
- Structured parsing of resume content into JSON
- Compare resume vs job description, with a fit score and tailored recommendations
- Download structured analysis as JSON

## Notes
- Some scanned PDFs may have poor extracted text. Consider providing a text version if results look incomplete.
- Models can be changed in the sidebar. `command-r` is a good default on Cohere. 