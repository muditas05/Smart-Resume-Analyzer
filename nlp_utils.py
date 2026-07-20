"""
nlp_utils.py
Keyword extraction, text cleaning, and resume-vs-job-description matching.
Uses spaCy for lemmatization/entity recognition, NLTK for stopwords,
and scikit-learn (TF-IDF + cosine similarity) for the match score.
"""

import re
import spacy
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- One-time resource setup -------------------------------------------------
try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords", quiet=True)

try:
    NLP = spacy.load("en_core_web_sm")
except OSError:
    # Model not downloaded yet — caller should run:
    # python -m spacy download en_core_web_sm
    raise OSError(
        "spaCy model 'en_core_web_sm' not found. Run: "
        "python -m spacy download en_core_web_sm"
    )

STOPWORDS = set(stopwords.words("english"))

# Words that are technically "nouns" but useless as resume/JD keywords
GENERIC_BLOCKLIST = {
    "experience", "work", "job", "team", "role", "company", "years",
    "year", "skill", "skills", "ability", "knowledge", "responsibility",
    "responsibilities", "requirement", "requirements", "candidate",
    "including", "etc", "using", "use", "strong", "excellent", "good",
}


def clean_text(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9\s\+\#\.\-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def extract_keywords(text: str, top_n: int = 40) -> list[str]:
    """
    Extract candidate keywords/skills from text using spaCy noun chunks
    and named entities, filtered against stopwords and a generic blocklist.
    """
    doc = NLP(clean_text(text))
    candidates = set()

    # Noun chunks capture multi-word skills like "machine learning"
    for chunk in doc.noun_chunks:
        term = chunk.text.strip().lower()
        term = " ".join(w for w in term.split() if w not in STOPWORDS)
        if term and len(term) > 2 and term not in GENERIC_BLOCKLIST:
            candidates.add(term)

    # Single-token nouns/proper nouns and known tech entities
    for token in doc:
        if token.pos_ in ("NOUN", "PROPN") and not token.is_stop:
            term = token.lemma_.lower().strip()
            if len(term) > 2 and term not in GENERIC_BLOCKLIST and term not in STOPWORDS:
                candidates.add(term)

    for ent in doc.ents:
        if ent.label_ in ("ORG", "PRODUCT", "LANGUAGE"):
            candidates.add(ent.text.strip().lower())

    return sorted(candidates)[:top_n]


def compute_match_score(resume_text: str, job_text: str) -> float:
    """
    TF-IDF + cosine similarity between resume and job description.
    Returns a percentage score (0-100).
    """
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform([clean_text(resume_text), clean_text(job_text)])
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(float(similarity) * 100, 1)


def keyword_gap_analysis(resume_text: str, job_text: str) -> dict:
    """
    Compares keywords extracted from the job description against those
    found in the resume, returning matched and missing sets.
    """
    resume_keywords = set(extract_keywords(resume_text, top_n=80))
    job_keywords = set(extract_keywords(job_text, top_n=60))

    matched = sorted(job_keywords & resume_keywords)
    missing = sorted(job_keywords - resume_keywords)

    return {
        "matched": matched,
        "missing": missing,
        "job_keyword_count": len(job_keywords),
        "coverage_pct": round(len(matched) / len(job_keywords) * 100, 1) if job_keywords else 0.0,
    }
