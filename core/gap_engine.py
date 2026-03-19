from __future__ import annotations

import re
from difflib import SequenceMatcher

from utils.llm_gemini import generate_json
from utils.normalizers import normalize_skills
from utils.prompts import JOB_SKILL_EXTRACTION_SYSTEM
from core.skill_engine import normalize_score


JD_KEYWORD_BANK = {
    "python",
    "java",
    "javascript",
    "typescript",
    "sql",
    "docker",
    "kubernetes",
    "aws",
    "gcp",
    "azure",
    "react",
    "nodejs",
    "fastapi",
    "flask",
    "django",
    "pandas",
    "numpy",
    "machine learning",
    "ci/cd",
    "system design",
}

SKILL_CLUSTERS = {
    "DevOps": {"docker", "kubernetes", "aws", "gcp", "azure", "ci/cd"},
    "Backend": {"python", "java", "nodejs", "fastapi", "flask", "django", "sql", "system design"},
    "Frontend": {"javascript", "typescript", "react"},
    "Data/ML": {"pandas", "numpy", "machine learning"},
}


def extract_job_skills(jd_text: str) -> list[str]:
    lowered = jd_text.lower()
    found = [skill for skill in JD_KEYWORD_BANK if re.search(rf"\b{re.escape(skill)}\b", lowered)]

    llm_payload = generate_json(
        system_prompt=JOB_SKILL_EXTRACTION_SYSTEM,
        user_prompt=f"Job Description:\n{jd_text}",
    )
    llm_skills = []
    if isinstance(llm_payload, dict):
        raw_skills = llm_payload.get("skills", [])
        if isinstance(raw_skills, list):
            llm_skills = [str(skill).strip().lower() for skill in raw_skills if str(skill).strip()]

    return normalize_skills(found + llm_skills)


def _best_similarity(skill: str, user_skills: list[str]) -> float:
    return max((SequenceMatcher(None, skill, user).ratio() for user in user_skills), default=0.0)


def _cluster_missing_skills(missing_skills: list[str]) -> dict[str, list[str]]:
    clustered: dict[str, list[str]] = {k: [] for k in SKILL_CLUSTERS}
    clustered["Other"] = []

    for skill in missing_skills:
        assigned = False
        for cluster_name, cluster_skills in SKILL_CLUSTERS.items():
            if skill in cluster_skills:
                clustered[cluster_name].append(skill)
                assigned = True
                break
        if not assigned:
            clustered["Other"].append(skill)

    return {k: v for k, v in clustered.items() if v}


def _extract_role_label(jd_text: str) -> str:
    first_line = jd_text.strip().splitlines()[0].strip() if jd_text.strip() else ""
    if first_line and len(first_line) <= 70:
        return first_line
    return "Target Role"


def build_gap_analysis(user_skill_conf: dict[str, float], jd_text: str) -> dict:
    jd_skills = extract_job_skills(jd_text)
    user_skills = list(user_skill_conf.keys())
    role_label = _extract_role_label(jd_text)

    if not jd_skills:
        return {
            "match_score": normalize_score(0),
            "missing_skills": [],
            "clusters": {},
            "recommendations": ["Add more detailed responsibilities to the job description."],
            "role_label": role_label,
        }

    matched = 0
    missing = []

    for jd_skill in jd_skills:
        similarity = _best_similarity(jd_skill, user_skills)
        if similarity >= 0.72:
            matched += 1
        else:
            missing.append(jd_skill)

    raw_score = (matched / len(jd_skills)) * 100
    match_score = normalize_score(raw_score)
    clusters = _cluster_missing_skills(missing)
    recommendations = [f"Focus on {skill} to improve role readiness." for skill in missing[:5]]

    return {
        "match_score": match_score,
        "missing_skills": missing,
        "clusters": clusters,
        "recommendations": recommendations,
        "role_label": role_label,
    }
