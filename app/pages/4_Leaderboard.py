import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from core.leaderboard_engine import build_leaderboard_insights
from storage.db import fetch_college_users


st.title("College Leaderboard")

profile = st.session_state.get("user_profile")
if not profile:
    st.warning("Complete onboarding on Home page first.")
    st.stop()

college = profile["college"]
df = fetch_college_users(college)

if df.empty:
    st.info("No leaderboard data available yet for this college.")
    st.stop()

branch_filter = st.selectbox("Branch Filter", ["All"] + sorted(df["branch"].fillna("NA").unique().tolist()))
year_filter = st.selectbox("Year Filter", ["All"] + sorted(df["year"].fillna("NA").unique().tolist()))

filtered = df.copy()
if branch_filter != "All":
    filtered = filtered[filtered["branch"].fillna("NA") == branch_filter]
if year_filter != "All":
    filtered = filtered[filtered["year"].fillna("NA") == year_filter]

filtered = filtered.sort_values("combined_score", ascending=False).reset_index(drop=True)
filtered["rank"] = filtered.index + 1

st.dataframe(
    filtered[["rank", "name", "resume_score", "github_score", "combined_score"]],
    use_container_width=True,
)

fig = px.histogram(filtered, x="combined_score", nbins=10, title="Combined Score Distribution")
st.plotly_chart(fig, use_container_width=True)

insights = build_leaderboard_insights(filtered)
for insight in insights:
    clean = str(insight).lstrip("- ")
    st.write(f"- {clean}")
