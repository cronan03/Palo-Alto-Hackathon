import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))


st.title("Resume and GitHub Score Dashboard")

profile = st.session_state.get("user_profile")
if not profile:
    st.warning("Complete onboarding on Home page first.")
    st.stop()

c1, c2, c3 = st.columns(3)
c1.metric("Resume Score", f"{profile['resume_score']:.1f}")
c2.metric("GitHub Score", f"{profile['github_score']:.1f}")
c3.metric("Combined Score", f"{profile['combined_score']:.1f}")

exp = profile.get("resume_experience", {})
projects = profile.get("resume_projects", [])

c4, c5 = st.columns(2)
c4.metric("Detected Experience (Years)", exp.get("years", 0))
c5.metric("Resume Projects Found", len(projects))

skills = profile.get("skills", {})
if skills:
    df = pd.DataFrame(
        [{"skill": skill, "confidence": score} for skill, score in skills.items()]
    ).sort_values("confidence", ascending=False)
    fig = px.bar(df.head(15), x="skill", y="confidence", title="Top Skills")
    st.plotly_chart(fig, use_container_width=True)

top_skills = sorted(skills.items(), key=lambda x: x[1], reverse=True)[:3]
weak_skills = sorted(skills.items(), key=lambda x: x[1])[:3]

st.subheader("Insights")
if top_skills:
    st.write("Strong areas:", ", ".join([s for s, _ in top_skills]))
if weak_skills:
    st.write("Low-confidence areas:", ", ".join([s for s, _ in weak_skills]))

if projects:
    st.subheader("Detected Project Highlights")
    for line in projects[:5]:
        # Avoid double bullets: many extracted lines already contain leading dashes
        clean = str(line).lstrip("- ")
        st.write(f"- {clean}")
