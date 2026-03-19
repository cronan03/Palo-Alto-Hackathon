from __future__ import annotations

import pandas as pd


def build_leaderboard_insights(df: pd.DataFrame) -> list[str]:
    if df.empty:
        return ["No users found for this cohort."]

    top_cut = max(1, int(len(df) * 0.1))
    top_avg = df.sort_values("combined_score", ascending=False).head(top_cut)["github_score"].mean()
    all_avg = df["github_score"].mean()

    insights = [
        f"Top 10% average GitHub score: {top_avg:.1f}.",
        f"Cohort average GitHub score: {all_avg:.1f}.",
    ]

    if top_avg > all_avg:
        insights.append("Top performers generally have stronger GitHub portfolios.")

    return insights
