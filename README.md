# 🤖📄 Smart Resume Analyzer

AI-Powered Resume Analysis and ATS Optimization System

## Features

- Resume Parsing
- ATS Score Analysis
- AI Resume Suggestions
- Cover Letter Generator
- Resume Visualization
- Keyword Matching

## Technologies

- Python
- Streamlit
- SQLite
- Google Gemini AI
- NLP
- Scikit-Learn

## Installation

````bash
pip install -r requirements.txt
streamlit run app.py<<<<<<< HEAD
# ResumeTailor AI

Tailor your resume to any job description: match scoring, keyword gap analysis,
AI-generated bullet rewrites and cover letters, and PDF/DOCX export.

## Stack

- **Frontend:** Streamlit + custom HTML/CSS/JS
- **Backend:** Python / Streamlit
- **Database:** SQLite
- **AI/NLP:** Gemini API, spaCy, NLTK
- **ML:** scikit-learn (TF-IDF + cosine similarity), Pandas
- **Visualization:** Plotly, Matplotlib
- **Document processing:** PyPDF2, python-docx, ReportLab
- **Deployment:** Docker / docker-compose

## Local setup

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -m nltk.downloader stopwords

cp .env.example .env          # then add your GEMINI_API_KEY
export GEMINI_API_KEY=xxxxx   # or use python-dotenv / your OS env manager

streamlit run app.py
````

App runs at http://localhost:8501

## Docker

```bash
export GEMINI_API_KEY=xxxxx
docker compose up --build
```

## Project structure

```
resumetailor/
├── app.py               # Streamlit UI and page routing
├── database.py           # SQLite models & queries
├── resume_parser.py      # PDF/DOCX/TXT text extraction
├── nlp_utils.py           # Keyword extraction + TF-IDF match scoring
├── ai_service.py           # Gemini API calls (suggestions, cover letters)
├── pdf_generator.py       # ReportLab/python-docx export
├── visualization.py        # Plotly/Matplotlib charts
├── automation.py            # Selenium job-posting scraper
├── static/style.css         # Custom CSS
├── data/                    # SQLite DB + generated assets (gitignored)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Notes

- Get a Gemini API key at https://aistudio.google.com/apikey
- `automation.py`'s URL scraper is a generic fallback — always check a job
  board's terms of service before scraping it, and prefer an official API
  where one exists.
- # SQLite data persists in `./data` (mounted as a volume in Docker).

# Smart-Resume-Analyzer

AI-Powered Resume Analysis and ATS Optimization System

> > > > > > > e9494814907d684d1938fab1019ee7ea10e32183
