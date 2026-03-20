import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from core.gap_engine import build_gap_analysis
from storage.db import init_db, save_job_match_run
from utils.graph_viz import render_knowledge_graph


st.title("Job Match and Skill Gap Analysis")
init_db()

profile = st.session_state.get("user_profile")
if not profile:
    st.warning("Complete onboarding on Home page first.")
    st.stop()

jd_text = st.text_area("Paste Job Description", height=220)

if st.button("Analyze Match"):
    if not jd_text.strip():
        st.error("Please paste a job description first.")
    else:
        with st.spinner("Analyzing your profile vs job description..."):
            result = build_gap_analysis(profile.get("skills", {}), jd_text)
            save_job_match_run(profile.get("github_username", "unknown"), jd_text, result)

        st.metric("Match Score", f"{result['match_score']:.0f}%")

        st.subheader("Missing Skills")
        if result["missing_skills"]:
            st.write(", ".join(result["missing_skills"]))
        else:
            st.success("No major missing skills detected for this role.")

        if result.get("clusters"):
            st.subheader("Gap Clusters")
            for cluster, skills in result["clusters"].items():
                st.write(f"- {cluster}: {', '.join(skills)}")

        st.subheader("Recommendations")
        for rec in result["recommendations"]:
            # Recommendations may already contain list markers; keep rendering to a single bullet
            clean = str(rec).lstrip("- ")
            st.write(f"- {clean}")

        st.subheader("Knowledge Graph")
        html = render_knowledge_graph(
            user_skills=list(profile.get("skills", {}).keys()),
            missing_skills=result["missing_skills"],
            role_label=result["role_label"],
        )
        st.components.v1.html(html, height=500, scrolling=True)
