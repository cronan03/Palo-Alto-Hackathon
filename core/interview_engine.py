from __future__ import annotations

from utils.llm_gemini import generate_json
from utils.prompts import ANSWER_EVAL_SYSTEM, QUESTION_GENERATION_SYSTEM


def generate_questions(profile: dict, jd_text: str, n: int = 5) -> list[dict]:
    llm_questions = _generate_questions_llm(profile, jd_text, n)
    if llm_questions:
        return llm_questions

    return _generate_questions_fallback(profile, jd_text, n)


def _generate_questions_fallback(profile: dict, jd_text: str, n: int = 5) -> list[dict]:
    skills = list(profile.get("skills", {}).keys())[:5]
    resume_skills = profile.get("resume_skills", [])[:3]
    missing_hint = "system design"
    if "kubernetes" in jd_text.lower():
        missing_hint = "kubernetes"

    templates = [
        ("resume", f"Explain one project where you used {resume_skills[0] if resume_skills else 'a core skill'} and your key trade-offs."),
        ("jd", f"How would you apply {skills[0] if skills else 'your strongest skill'} in this target role?"),
        ("gap", f"You appear to have less exposure to {missing_hint}. How would you learn and apply it in 30 days?"),
        ("scenario", "Design a scalable backend service for one of your projects. Walk through architecture and bottlenecks."),
        ("depth", f"What is one technical decision you would change in a past project using {skills[1] if len(skills) > 1 else 'your toolkit'}?")
    ]

    questions = []
    for idx, (category, q) in enumerate(templates[: max(1, n)], start=1):
        questions.append({"id": idx, "category": category, "question": q})
    return questions


def _generate_questions_llm(profile: dict, jd_text: str, n: int) -> list[dict]:
    prompt = (
        f"N={n}\n\n"
        f"Candidate Skills: {list(profile.get('skills', {}).keys())}\n"
        f"Candidate Resume Skills: {profile.get('resume_skills', [])}\n"
        f"Candidate Projects: {profile.get('resume_projects', [])}\n"
        f"Candidate Experience: {profile.get('resume_experience', {})}\n\n"
        f"Job Description:\n{jd_text}"
    )

    payload = generate_json(
        system_prompt=QUESTION_GENERATION_SYSTEM,
        user_prompt=prompt,
        temperature=0.3,
    )
    if not isinstance(payload, dict):
        return []

    raw_questions = payload.get("questions", [])
    if not isinstance(raw_questions, list):
        return []

    questions = []
    for idx, item in enumerate(raw_questions[: max(1, n)], start=1):
        if not isinstance(item, dict):
            continue
        question = str(item.get("question", "")).strip()
        category = str(item.get("category", "jd")).strip().lower() or "jd"
        if question:
            questions.append({"id": idx, "category": category, "question": question})
    return questions


def evaluate_answer(question: dict, answer: str) -> dict:
    llm_eval = _evaluate_answer_llm(question, answer)
    if llm_eval:
        return llm_eval

    return _evaluate_answer_fallback(question, answer)


def _evaluate_answer_fallback(question: dict, answer: str) -> dict:
    answer = (answer or "").strip()
    word_count = len(answer.split())

    base = 3
    if word_count > 50:
        base += 2
    if any(token in answer.lower() for token in ["because", "trade-off", "latency", "scale", "testing"]):
        base += 2
    if any(token in answer.lower() for token in ["docker", "kubernetes", "ci/cd", "api", "database"]):
        base += 1

    score = max(1, min(10, base))
    strengths = ["Clear structure"] if word_count > 30 else ["Concise response"]
    weaknesses = ["Needs deeper technical detail"] if score < 7 else ["Could include measurable outcomes"]
    suggestion = "Use concrete metrics, system constraints, and trade-offs in your response."

    return {
        "score_total": score,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "improvement_suggestion": suggestion,
    }


def _evaluate_answer_llm(question: dict, answer: str) -> dict | None:
    prompt = (
        f"Question Category: {question.get('category', 'unknown')}\n"
        f"Question: {question.get('question', '')}\n\n"
        f"Candidate Answer:\n{answer}"
    )

    payload = generate_json(
        system_prompt=ANSWER_EVAL_SYSTEM,
        user_prompt=prompt,
        temperature=0.2,
    )
    if not isinstance(payload, dict):
        return None

    score_total = payload.get("score_total")
    strengths = payload.get("strengths", [])
    weaknesses = payload.get("weaknesses", [])
    improvement = payload.get("improvement_suggestion", "")

    try:
        score_total = int(round(float(score_total)))
    except Exception:
        return None

    score_total = max(1, min(10, score_total))

    if not isinstance(strengths, list):
        strengths = ["Response attempts to address the prompt"]
    if not isinstance(weaknesses, list):
        weaknesses = ["Needs clearer structure and depth"]

    strengths = [str(x).strip() for x in strengths if str(x).strip()][:3]
    weaknesses = [str(x).strip() for x in weaknesses if str(x).strip()][:3]
    improvement_suggestion = str(improvement).strip() or "Use concrete examples, constraints, and trade-offs."

    return {
        "score_total": score_total,
        "strengths": strengths or ["Answer is relevant to the question"],
        "weaknesses": weaknesses or ["Needs stronger technical depth"],
        "improvement_suggestion": improvement_suggestion,
    }


def summarize_interview(evaluations: list[dict]) -> dict:
    if not evaluations:
        return {
            "overall_score": 0,
            "strengths": [],
            "weaknesses": [],
            "focus_areas": [],
        }

    avg_score = round(sum(e["score_total"] for e in evaluations) / len(evaluations), 2)

    strengths = []
    weaknesses = []
    for e in evaluations:
        strengths.extend(e.get("strengths", []))
        weaknesses.extend(e.get("weaknesses", []))

    return {
        "overall_score": avg_score,
        "strengths": sorted(set(strengths))[:4],
        "weaknesses": sorted(set(weaknesses))[:4],
        "focus_areas": ["System design", "Deployment", "Scalability"],
    }
