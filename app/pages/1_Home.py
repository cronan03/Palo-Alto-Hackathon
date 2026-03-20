import io
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from core.github_parser import compute_github_score, get_repos, infer_skills
from core.resume_parser import extract_experience, extract_projects, extract_skills, extract_text
from core.skill_engine import build_unified_skill_profile, compute_resume_score
from storage.db import init_db, upsert_user_profile


st.title("Home - Onboarding")
st.caption("Upload your resume and connect GitHub to generate your skill profile.")

init_db()

with st.form("onboard_form"):
    name = st.text_input("Name")
    college = st.text_input("College Name")
    branch = st.text_input("Branch (optional)")
    year = st.text_input("Graduation Year (optional)")
    github_username = st.text_input("GitHub Username")
    resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    submit = st.form_submit_button("Analyze Profile")

if submit:
    if not name or not college or not github_username or resume_file is None:
        st.error("Name, college, GitHub username, and resume are required.")
    else:
        with st.spinner("Analyzing your resume and GitHub profile..."):
            resume_bytes = resume_file.read()
            resume_text = extract_text(io.BytesIO(resume_bytes))
            resume_skills = extract_skills(resume_text)
            resume_projects = extract_projects(resume_text)
            resume_experience = extract_experience(resume_text)

            repos = get_repos(github_username)
            github_skills = infer_skills(repos)
            github_score = compute_github_score(repos, github_skills)
            resume_score = compute_resume_score(resume_skills, resume_text)

            unified_profile = build_unified_skill_profile(
                resume_skills=resume_skills,
                github_skills=github_skills,
                resume_score=resume_score,
                github_score=github_score,
            )

            st.session_state["user_profile"] = {
                "name": name,
                "college": college,
                "branch": branch,
                "year": year,
                "github_username": github_username,
                "resume_text": resume_text,
                "resume_skills": resume_skills,
                "resume_projects": resume_projects,
                "resume_experience": resume_experience,
                "github_skills": github_skills,
                "resume_score": resume_score,
                "github_score": github_score,
                "combined_score": unified_profile["combined_score"],
                "skills": unified_profile["skills"],
            }

            upsert_user_profile(st.session_state["user_profile"])

        st.success("Profile created successfully. Redirecting to the Dashboard...")
        # st.json(
        #     {
        #         "resume_score": round(resume_score, 2),
        #         "github_score": round(github_score, 2),
        #         "combined_score": round(unified_profile["combined_score"], 2),
        #     }
        # )
        st.switch_page("pages/2_Dashboard.py")
