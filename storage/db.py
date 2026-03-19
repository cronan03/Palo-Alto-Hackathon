from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


DB_PATH = Path(__file__).resolve().parents[1] / "skill_bridge.db"


def _conn() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            github_username TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            college TEXT NOT NULL,
            branch TEXT,
            year TEXT,
            resume_score REAL,
            github_score REAL,
            combined_score REAL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS job_match_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            github_username TEXT NOT NULL,
            job_description TEXT NOT NULL,
            match_score REAL,
            missing_skills_json TEXT,
            clusters_json TEXT,
            recommendations_json TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS interview_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            github_username TEXT NOT NULL,
            job_description TEXT NOT NULL,
            questions_json TEXT,
            evaluations_json TEXT,
            summary_json TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def upsert_user_profile(profile: dict) -> None:
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO users (github_username, name, college, branch, year, resume_score, github_score, combined_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(github_username) DO UPDATE SET
            name=excluded.name,
            college=excluded.college,
            branch=excluded.branch,
            year=excluded.year,
            resume_score=excluded.resume_score,
            github_score=excluded.github_score,
            combined_score=excluded.combined_score
        """,
        (
            profile["github_username"],
            profile["name"],
            profile["college"],
            profile.get("branch"),
            profile.get("year"),
            profile.get("resume_score", 0.0),
            profile.get("github_score", 0.0),
            profile.get("combined_score", 0.0),
        ),
    )
    conn.commit()
    conn.close()


def fetch_college_users(college: str) -> pd.DataFrame:
    conn = _conn()
    df = pd.read_sql_query(
        "SELECT name, branch, year, resume_score, github_score, combined_score FROM users WHERE college = ?",
        conn,
        params=(college,),
    )
    conn.close()
    return df


def save_job_match_run(github_username: str, jd_text: str, result: dict) -> None:
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO job_match_runs (
            github_username,
            job_description,
            match_score,
            missing_skills_json,
            clusters_json,
            recommendations_json,
            created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            github_username,
            jd_text,
            result.get("match_score", 0.0),
            json.dumps(result.get("missing_skills", [])),
            json.dumps(result.get("clusters", {})),
            json.dumps(result.get("recommendations", [])),
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()
    conn.close()


def save_interview_run(
    github_username: str,
    jd_text: str,
    questions: list[dict],
    evaluations: list[dict],
    summary: dict,
) -> None:
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO interview_runs (
            github_username,
            job_description,
            questions_json,
            evaluations_json,
            summary_json,
            created_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            github_username,
            jd_text,
            json.dumps(questions),
            json.dumps(evaluations),
            json.dumps(summary),
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()
    conn.close()
