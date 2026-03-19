from __future__ import annotations


SKILL_ALIASES = {
    "node": "nodejs",
    "node.js": "nodejs",
    "js": "javascript",
    "ts": "typescript",
    "ml": "machine learning",
    "k8s": "kubernetes",
    "postgres": "sql",
}


def normalize_skill(skill: str) -> str:
    cleaned = (skill or "").strip().lower()
    return SKILL_ALIASES.get(cleaned, cleaned)


def normalize_skills(skills: list[str]) -> list[str]:
    return sorted(set(normalize_skill(s) for s in skills if s and str(s).strip()))
