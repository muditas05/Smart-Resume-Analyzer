"""
database.py
SQLite persistence layer for ResumeTailor AI.
Handles users, saved resumes, job descriptions, and analysis history.
"""

import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager

DB_PATH = "data/resumeanalyzer.db"


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Create tables if they don't already exist. Safe to call on every app start."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                raw_text TEXT NOT NULL,
                file_type TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS job_descriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT,
                company TEXT,
                raw_text TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                resume_id INTEGER,
                job_id INTEGER,
                match_score REAL,
                matched_keywords TEXT,
                missing_keywords TEXT,
                ai_suggestions TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (resume_id) REFERENCES resumes(id),
                FOREIGN KEY (job_id) REFERENCES job_descriptions(id)
            )
        """)
        conn.commit()


def get_or_create_user(username: str) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        if row:
            return row["id"]
        cur.execute(
            "INSERT INTO users (username, created_at) VALUES (?, ?)",
            (username, datetime.utcnow().isoformat()),
        )
        return cur.lastrowid


def save_resume(user_id: int, title: str, raw_text: str, file_type: str) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO resumes (user_id, title, raw_text, file_type, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, title, raw_text, file_type, datetime.utcnow().isoformat()),
        )
        return cur.lastrowid


def save_job_description(user_id: int, title: str, company: str, raw_text: str) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO job_descriptions (user_id, title, company, raw_text, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, title, company, raw_text, datetime.utcnow().isoformat()),
        )
        return cur.lastrowid


def save_analysis(user_id, resume_id, job_id, match_score, matched_keywords,
                   missing_keywords, ai_suggestions) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO analyses
            (user_id, resume_id, job_id, match_score, matched_keywords, missing_keywords, ai_suggestions, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, resume_id, job_id, match_score,
            json.dumps(matched_keywords), json.dumps(missing_keywords),
            json.dumps(ai_suggestions), datetime.utcnow().isoformat()
        ))
        return cur.lastrowid


def get_user_history(user_id: int, limit: int = 20):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT a.id, a.match_score, a.created_at,
                   r.title AS resume_title, j.title AS job_title, j.company
            FROM analyses a
            LEFT JOIN resumes r ON a.resume_id = r.id
            LEFT JOIN job_descriptions j ON a.job_id = j.id
            WHERE a.user_id = ?
            ORDER BY a.created_at DESC
            LIMIT ?
        """, (user_id, limit))
        return [dict(row) for row in cur.fetchall()]


def get_user_resumes(user_id: int):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM resumes WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        return [dict(row) for row in cur.fetchall()]

