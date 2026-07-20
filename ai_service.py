"""
ai_service.py
Wraps calls to the Gemini API for AI-generated resume feedback,
bullet-point rewrites, and tailored cover letter drafts.

Requires GEMINI_API_KEY to be set as an environment variable.
"""

import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

MODEL_NAME = "gemini-2.0-flash"


def _get_model():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY is not set. Add it to your environment or .env file."
        )
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(MODEL_NAME)


def generate_resume_suggestions(resume_text: str, job_text: str, missing_keywords: list[str]) -> dict:
    """
    Asks Gemini for structured, actionable suggestions to tailor the resume
    to the job description. Returns a dict parsed from JSON.
    """
    model = _get_model()

    prompt = f"""You are an expert career coach and resume writer.

Compare the RESUME to the JOB DESCRIPTION below and produce actionable,
specific tailoring advice. Focus especially on these missing keywords
the resume should try to naturally incorporate where truthful: {missing_keywords}

Return ONLY valid JSON (no markdown fences, no preamble) with this exact shape:
{{
  "summary": "2-3 sentence overview of fit and biggest gaps",
  "bullet_rewrites": [
    {{"original": "...", "improved": "...", "reason": "..."}}
  ],
  "keywords_to_add": ["..."],
  "sections_to_improve": ["..."]
}}

RESUME:
{resume_text[:6000]}

JOB DESCRIPTION:
{job_text[:4000]}
"""

    response = model.generate_content(prompt)
    raw = response.text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "summary": raw,
            "bullet_rewrites": [],
            "keywords_to_add": missing_keywords,
            "sections_to_improve": [],
        }


def generate_cover_letter(resume_text: str, job_text: str, company: str, tone: str = "professional") -> str:
    model = _get_model()

    prompt = f"""Write a {tone}, concise cover letter (under 300 words) for the job
described below, based on the candidate's resume. Address it generically
(no placeholder brackets left unfilled except [Hiring Manager] if the name
is unknown). Company: {company or "the company"}.

RESUME:
{resume_text[:5000]}

JOB DESCRIPTION:
{job_text[:3000]}
"""
    response = model.generate_content(prompt)
    return response.text.strip()


def generate_interview_prep(job_text: str, resume_text: str, num_questions: int = 8) -> list[str]:
    model = _get_model()

    prompt = f"""Based on this job description and the candidate's resume,
generate {num_questions} likely interview questions the candidate should
prepare for. Mix behavioral and technical questions relevant to the role.
Return ONLY a JSON array of strings, no markdown fences.

JOB DESCRIPTION:
{job_text[:3000]}

RESUME:
{resume_text[:3000]}
"""
    response = model.generate_content(prompt)
    raw = response.text.strip().replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return [line.strip("- ") for line in raw.split("\n") if line.strip()]
