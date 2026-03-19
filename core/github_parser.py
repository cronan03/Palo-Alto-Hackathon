from __future__ import annotations

from collections import Counter

import requests

from utils.normalizers import normalize_skills


GITHUB_API = "https://api.github.com"


def get_repos(username: str) -> list[dict]:
    url = f"{GITHUB_API}/users/{username}/repos"
    params = {"per_page": 50, "sort": "updated"}
    try:
        resp = requests.get(url, params=params, timeout=12)
        if resp.status_code != 200:
            return []
        repos = resp.json()
        return repos if isinstance(repos, list) else []
    except Exception:
        return []


def infer_skills(repos: list[dict]) -> dict[str, float]:
    if not repos:
        return {}

    counter: Counter[str] = Counter()
    for repo in repos:
        lang = (repo.get("language") or "").lower().strip()
        if lang:
            counter[lang] += 2

        topics = repo.get("topics", []) or []
        for topic in topics:
            topic_clean = str(topic).strip().lower()
            if topic_clean:
                counter[topic_clean] += 1

        name = str(repo.get("name", "")).lower()
        if "ml" in name or "machine-learning" in name:
            counter["machine learning"] += 1

    normalized = normalize_skills(list(counter.keys()))
    if not normalized:
        return {}

    max_val = max(counter.values())
    return {skill: round(counter.get(skill, 1) / max_val, 3) for skill in normalized}


def compute_github_score(repos: list[dict], github_skills: dict[str, float]) -> float:
    if not repos:
        return 0.0

    repo_count_score = min(len(repos), 20) / 20 * 40
    stars = sum(int(r.get("stargazers_count", 0) or 0) for r in repos)
    star_score = min(stars, 50) / 50 * 15
    skill_depth_score = min(len(github_skills), 20) / 20 * 45
    return round(repo_count_score + star_score + skill_depth_score, 2)
