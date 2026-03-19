from __future__ import annotations


def compute_resume_score(resume_skills: list[str], resume_text: str) -> float:
    skill_coverage = min(len(resume_skills), 20) / 20 * 60
    richness = min(len(resume_text.split()), 800) / 800 * 40 if resume_text else 0
    return round(skill_coverage + richness, 2)


def build_unified_skill_profile(
    resume_skills: list[str],
    github_skills: dict[str, float],
    resume_score: float,
    github_score: float,
) -> dict:
    combined_score = round(0.6 * github_score + 0.4 * resume_score, 2)

    resume_weight = 0.4
    github_weight = 0.6

    merged: dict[str, float] = {}

    for skill in resume_skills:
        merged[skill] = max(merged.get(skill, 0), resume_weight)

    for skill, conf in github_skills.items():
        github_conf = min(1.0, max(0.0, conf))
        merged[skill] = round(max(merged.get(skill, 0), github_weight * github_conf), 3)

    return {
        "combined_score": combined_score,
        "skills": dict(sorted(merged.items(), key=lambda x: x[1], reverse=True)),
    }
