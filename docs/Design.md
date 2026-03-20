# Skill-Bridge Career Navigator — Design Document

## 1. Purpose & Scope

Skill-Bridge Career Navigator is a Streamlit-based assistant that helps students and early-career engineers understand their current readiness, identify job-fit gaps, and practice interviews. This document describes the end-to-end design of the MVP currently implemented in this repository.

## 2. Product Goals

- Parse resume PDFs and recent GitHub activity to construct a unified skill profile.
- Surface readiness metrics (Resume, GitHub, Combined) on a normalized 0–100 scale for easy interpretation.
- Given a target job description, highlight missing skills, cluster them, and offer recommendations + graph visualization.
- Provide a guided interview practice loop (“Resume Griller”) with contextual questions and AI-based answer evaluation.
- Persist data for future analytics (leaderboards, history) without external dependencies.

## 3. System Overview

```
User Resume + GitHub Handle
        │
        ▼
+---------------------+
| Parsing Layer       |
| - core.resume_parser|
| - core.github_parser|
+---------------------+
        │
        ▼
+---------------------+
| Skill Engine        |
| - core.skill_engine |
+---------------------+
        │
        ├───────────────▶ Job Match (core.gap_engine)
        │                 └─ Uses Gemini for JD skill extraction + fallbacks
        │
        └───────────────▶ Resume Griller (core.interview_engine)
                          └─ Gemini for question/evaluation + fallbacks
```

The Streamlit multipage UI (`app/pages/*`) orchestrates user flows, while `storage/db.py` manages SQLite persistence.

## 4. Key Components

### 4.1 Resume Parser (`core/resume_parser.py`)

- **extract_text**: Uses `pypdf` to read every page and returns the combined text.
- **extract_skills**: Regex matches against a curated skill bank, then normalizes tokens.
- **extract_projects**: Captures lines with verbs such as "project", "built", "developed" and trims to 20 entries.
- **extract_experience**: Finds `X years` patterns and stores bullet lines referencing internships/roles; leadership bullets must start with “Spearheaded”, “Instructed”, or “Directed”.
- Output feeds the Dashboard’s resume highlights table.

### 4.2 GitHub Analyzer (`core/github_parser.py`)

- **get_repos**: Calls GitHub REST API (`/users/{user}/repos`), sorted by `updated`, up to 50 repos.
- **infer_skills**: Counts languages (weight 2), topics (weight 1), and ML hints in repo names; values normalized to 0–1.
- **compute_github_score**: Mixes repo count, star count, and skill diversity (40/15/45 weighting) and normalizes via `normalize_score`.

### 4.3 Skill Engine (`core/skill_engine.py`)

- **compute_resume_score**: 60% skill coverage (max 20 unique skills) + 40% resume richness (max 800 words), then normalized.
- **build_unified_skill_profile**: Merges resume + GitHub skills with weighted confidences (0.4 vs 0.6) and computes the combined score (`0.6 * github + 0.4 * resume`).

### 4.4 Job Match Engine (`core/gap_engine.py`)

- Extracts JD skills using a hybrid approach: keyword bank + Gemini (`JOB_SKILL_EXTRACTION_SYSTEM`).
- Compares JD skills vs user skills using `SequenceMatcher`; similarity ≥ 0.72 counts as a match.
- Calculates raw match %, normalizes it, clusters missing skills (DevOps, Backend, Frontend, Data/ML, Other), and emits recommendations + role label.
- UI shows match score, missing skills, clusters, recommendations, and a PyVis graph.

### 4.5 Resume Griller (`core/interview_engine.py`)

- **generate_questions**: Prefers Gemini (`QUESTION_GENERATION_SYSTEM`), falls back to deterministic templates referencing resume skills, JD requirements, and gap hints.
- **evaluate_answer**: Gemini (`ANSWER_EVAL_SYSTEM`) for rubric scoring; fallback uses heuristics (word count, keyword presence) to rate 1–10.
- **summarize_interview**: Averages scores and aggregates strengths/weaknesses for final summary.

### 4.6 Streamlit UI (`app/pages/*`)

- `1_Home`: Onboarding form with spinner; creates `user_profile` in `st.session_state` and persists to SQLite, then redirects to the Dashboard.
- `2_Dashboard`: Spinner-wrapped insights showing donut charts for scores, AI-generated pros/cons, curated resource recommendations, and resume highlights table.
- `3_Job_Match`: Text area for JD, spinner-wrapped analysis, metrics, missing skills list, cluster bullets, and knowledge graph.
- `4_Leaderboard`: Renders rankings and histograms (not detailed here).
- `5_Resume_Griller`: Manages stateful interview session with question prompts, answer inputs, evaluations, and summary.

## 5. LLM Integration Strategy

- Wrapper: `utils.llm_gemini.generate_json` loads `GEMINI_API_KEY`, logs every call, prints raw responses, and returns parsed JSON or `None`.
- Prompts live in `utils/prompts.py` (job skills, dashboard insights, interview question generation, answer evaluation).
- Fallbacks exist for every LLM feature to guarantee usability without an API key.

## 6. Data Persistence

- SQLite via `storage/db.py` tracks users, job match runs, and interview sessions.
- Tables are initialized on first load of each page (`init_db()`); write helpers like `save_job_match_run` ensure traces for future analytics.

## 7. UX Design Choices

- Normalized score gauges keep stakeholder-facing metrics simple.
- Streamlit spinners highlight heavy operations (profile analysis, dashboard prep, job match).
- Donut charts emphasize scores in the center; resume highlights live in a table with pastel accents.
- Resource recommendations map weak skills to well-known learning links.

## 8. Trade-offs & Considerations

- **Hybrid parsing (heuristics + LLM)** gives deterministic performance with AI enhancements; pure LLM parsing was avoided to prevent latency issues.

## 9. Future Enhancements

1. Embedding-based JD similarity to reduce false matches/misses.
2. Richer GitHub signals (README text, commit cadence).
3. Authentication + multi-user dashboards.
4. Historical analytics (job match history, interview history) with dedicated pages.
5. Automated test suite covering parsers, scoring, and LLM fallbacks.

## 10. References

- Demo Video: https://youtu.be/WMdn5NLTvNc
- README: `README.md` (project overview + setup)
- Prompt definitions: `utils/prompts.py`

---

