from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from utils.llm_gemini import generate_json, has_gemini_api_key
from utils.prompts import PROFILE_INSIGHTS_SYSTEM


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
experience_highlights = exp.get("highlights", []) or []
leadership_highlights = exp.get("leadership", []) or []


def _clean_highlights(items: list[str], limit: int = 8) -> list[str]:
    cleaned: list[str] = []
    for raw in items:
        text = str(raw).lstrip("-• \t").strip()
        if len(text.split()) <= 1:
            continue
        if text:
            cleaned.append(text)
        if len(cleaned) >= limit:
            break
    return cleaned

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

# Baseline deterministic insights
if top_skills:
    st.write("Strong areas:", ", ".join([s for s, _ in top_skills]))
if weak_skills:
    st.write("Low-confidence areas:", ", ".join([s for s, _ in weak_skills]))

# Optional LLM-powered narrative insights
if has_gemini_api_key() and skills:
    with st.expander("AI-generated detailed insights", expanded=True):
        try:
            prompt = (
                "Candidate Profile for Insights\n\n"
                f"Name: {profile.get('name', 'Unknown')}\n"
                f"GitHub Username: {profile.get('github_username', 'unknown')}\n\n"
                f"Top Skills: {[s for s, _ in top_skills]}\n"
                f"Low-confidence Skills: {[s for s, _ in weak_skills]}\n\n"
                f"All Skills (with scores 0-1): {profile.get('skills', {})}\n\n"
                f"Resume Projects: {profile.get('resume_projects', [])}\n\n"
                f"Experience Summary: {profile.get('resume_experience', {})}"
            )

            payload = generate_json(
                system_prompt=PROFILE_INSIGHTS_SYSTEM,
                user_prompt=prompt,
                temperature=0.35,
            )

            if isinstance(payload, dict):
                summary = str(payload.get("summary", "")).strip()
                strengths = payload.get("strengths", []) or []
                gaps = payload.get("gaps", []) or []
                recs = payload.get("recommendations", []) or []

                if summary:
                    st.markdown(f"**Summary**: {summary}")
                # Pros/cons layout for AI insights
                if strengths or gaps:
                    st.markdown(
                        """
                        <style>
                        .ai-pro-item {
                            background-color: rgba(34, 197, 94, 0.12);
                            border-left: 3px solid #22c55e;
                            padding: 0.4rem 0.6rem;
                            border-radius: 0.35rem;
                            margin-bottom: 0.25rem;
                            font-size: 0.9rem;
                        }
                        .ai-con-item {
                            background-color: rgba(248, 113, 113, 0.12);
                            border-left: 3px solid #f97373;
                            padding: 0.4rem 0.6rem;
                            border-radius: 0.35rem;
                            margin-bottom: 0.25rem;
                            font-size: 0.9rem;
                        }
                        </style>
                        """,
                        unsafe_allow_html=True,
                    )

                    pros_col, cons_col = st.columns(2)

                    if strengths:
                        with pros_col:
                            st.markdown("**Pros (AI)**")
                            for item in strengths[:5]:
                                text = str(item).strip()
                                if text:
                                    st.markdown(
                                        f"<div class='ai-pro-item'>{text}</div>",
                                        unsafe_allow_html=True,
                                    )

                    if gaps:
                        with cons_col:
                            st.markdown("**Cons (AI)**")
                            for item in gaps[:5]:
                                text = str(item).strip()
                                if text:
                                    st.markdown(
                                        f"<div class='ai-con-item'>{text}</div>",
                                        unsafe_allow_html=True,
                                    )

                if recs:
                    st.markdown("**Recommended next steps (30–60 days)**")
                    for item in recs[:6]:
                        st.write(f"- {str(item).strip()}")
            else:
                st.caption("LLM insights unavailable right now; showing basic metric-based insights only.")
        except Exception:
            st.caption("LLM insights failed to load; falling back to basic insights.")

if projects or experience_highlights or leadership_highlights:
    st.subheader("Resume Highlights")

    project_rows = _clean_highlights(projects)
    experience_rows = _clean_highlights(experience_highlights)
    leadership_rows = _clean_highlights(leadership_highlights)
    row_count = max(len(project_rows), len(experience_rows), len(leadership_rows))

    st.markdown(
        """
        <style>
        .resume-table {
            width: 100%;
            border-collapse: collapse;
            overflow: hidden;
            border-radius: 12px;
            background: rgba(99, 102, 241, 0.08);
        }
        .resume-table th {
            text-align: left;
            padding: 0.65rem;
            font-size: 0.95rem;
            background: rgba(76, 29, 149, 0.3);
            color: #f9fafb;
        }
        .resume-table td {
            padding: 0.6rem;
            font-size: 0.9rem;
            vertical-align: top;
            color: #e5e7eb;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
        }
        .resume-table tr:nth-child(even) {
            background: rgba(15, 23, 42, 0.35);
        }
        .resume-empty {
            color: rgba(226, 232, 240, 0.6);
            font-style: italic;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if row_count == 0:
        st.caption("No resume highlights detected yet. Upload a richer resume to populate this section.")
    else:
        rows_html = []
        for idx in range(row_count):
            proj = project_rows[idx] if idx < len(project_rows) else ""
            exp_item = experience_rows[idx] if idx < len(experience_rows) else ""
            lead = leadership_rows[idx] if idx < len(leadership_rows) else ""
            rows_html.append(
                "<tr>"
                f"<td>{proj or '<span class=\"resume-empty\">—</span>'}</td>"
                f"<td>{exp_item or '<span class=\"resume-empty\">—</span>'}</td>"
                f"<td>{lead or '<span class=\"resume-empty\">—</span>'}</td>"
                "</tr>"
            )

        table_html = (
            "<table class='resume-table'>"
            "<thead><tr>"
            "<th>Projects</th><th>Experience</th><th>Leadership</th>"
            "</tr></thead>"
            f"<tbody>{''.join(rows_html)}</tbody>"
            "</table>"
        )
        st.markdown(table_html, unsafe_allow_html=True)
