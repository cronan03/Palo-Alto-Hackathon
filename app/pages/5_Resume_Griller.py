import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from core.interview_engine import evaluate_answer, generate_questions, summarize_interview
from storage.db import init_db, save_interview_run


st.title("Resume Griller")
init_db()

profile = st.session_state.get("user_profile")
if not profile:
    st.warning("Complete onboarding on Home page first.")
    st.stop()

jd_text = st.text_area("Paste target Job Description", height=180)

if "griller_state" not in st.session_state:
    st.session_state["griller_state"] = {
        "questions": [],
        "answers": [],
        "evaluations": [],
        "index": 0,
        "active": False,
    }

state = st.session_state["griller_state"]

if st.button("Start Interview"):
    if not jd_text.strip():
        st.error("Please provide a job description first.")
    else:
        state["questions"] = generate_questions(profile, jd_text, n=5)
        state["answers"] = []
        state["evaluations"] = []
        state["index"] = 0
        state["active"] = True

if state["active"] and state["index"] < len(state["questions"]):
    current_q = state["questions"][state["index"]]
    st.subheader(f"Question {state['index'] + 1}")
    st.write(current_q["question"])

    answer = st.text_area("Your answer", key=f"answer_{state['index']}")
    if st.button("Submit Answer", key=f"submit_{state['index']}"):
        evaluation = evaluate_answer(current_q, answer)
        state["answers"].append(answer)
        state["evaluations"].append(evaluation)

        st.write(f"Score: {evaluation['score_total']}/10")
        st.write("Strengths:", ", ".join(evaluation["strengths"]))
        st.write("Weaknesses:", ", ".join(evaluation["weaknesses"]))
        st.write("Suggestion:", evaluation["improvement_suggestion"])

        state["index"] += 1

if state["active"] and state["index"] >= len(state["questions"]):
    st.subheader("Final Interview Summary")
    summary = summarize_interview(state["evaluations"])

    save_interview_run(
        github_username=profile.get("github_username", "unknown"),
        jd_text=jd_text,
        questions=state["questions"],
        evaluations=state["evaluations"],
        summary=summary,
    )

    st.json(summary)
    state["active"] = False
