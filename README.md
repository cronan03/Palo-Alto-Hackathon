# Skill-Bridge Career Navigator

AI-powered career intelligence for students and early-career professionals. Upload a resume, connect GitHub, and receive a unified snapshot of demonstrated skills, job-fit guidance, and targeted interview practice.

---

## Feature Snapshot

- **Guided Onboarding** (Home page): resume upload + GitHub username produces a unified skill profile with normalized scores (every metric is scaled into the 70–100 band for easy comparison).
- **Insights Dashboard**: top skills bar chart, AI-generated pros/cons, and structured resume highlights (projects, experience, leadership) directly extracted from the PDF.
- **Job Match & Gap Analysis**: hybrid heuristic + Gemini flow that extracts JD skills, computes a normalized match score, clusters gaps, and renders a knowledge graph.
- **Resume Griller**: contextual interview practice with Gemini-based question generation & answer evaluation plus deterministic fallbacks.
- **College Leaderboard**: cohort benchmarking with filters, score histogram, and persistence for trend tracking.
- **Persistence Layer**: SQLite-backed storage of user profiles, job match runs, and interview runs for quick iteration.

> **Score normalization**: Resume, GitHub, and Job Match scores are internally computed on 0–100, then linearly rescaled to 70–100 so reviewers always see “at a glance” readiness levels on a consistent scale.

---

## Repository Layout

```
app/
  main.py              # Streamlit entry point (forwards to Home page)
  pages/
   1_Home.py          # Resume/GitHub onboarding
   2_Dashboard.py     # Scores, AI insights, resume highlights
   3_Job_Match.py     # Job-fit analysis + knowledge graph
   4_Leaderboard.py   # College leaderboard & histogram
   5_Resume_Griller.py# Interview simulation
core/                  # Resume/GitHub parsers, scoring engines, gap analysis
utils/                 # Prompts, normalizers, graph rendering helpers
storage/               # SQLite helpers
data/                  # Taxonomies / seed data
tests/                 # (placeholder) engine-level tests
```

---

## Local Setup

1. **Create & activate a virtual environment**

```powershell
cd hack
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. **Install dependencies**

```powershell
pip install -r requirements.txt
```

3. **Configure Gemini** (see below)
4. **Launch the app**

```powershell
streamlit run app/main.py
```

When the Streamlit server starts it will open the **Home** page automatically. Complete onboarding once; subsequent pages pull data from `st.session_state`.

---

## Gemini / LLM Configuration

Create `.env` (or edit the existing one) in the repo root:

```env
GEMINI_API_KEY=your_real_key
GEMINI_MODEL=gemini-3-flash-preview  # or gemini-1.5-flash
```

Behavior:

- If `GEMINI_API_KEY` is set, Job Match skill extraction, Dashboard AI insights, and Resume Griller use Gemini responses (with raw-response logging in the terminal for debugging).
- If the key is missing or the API fails, each feature automatically falls back to deterministic heuristics so the UX stays functional.

> Logging tip: the Streamlit terminal prints `[Gemini] ...` whenever the helper is called. This is useful for verifying real LLM usage during demos.

---

## Running Tests / Quality Checks

Formal tests are still being built. For now, sanity-check the engines via the Streamlit UI:

1. Onboard a sample resume + GitHub username.
2. Visit Dashboard to verify normalized metrics and AI insights.
3. Paste a job description in Job Match and confirm the new match score range (70–100) plus the gap clusters & graph.
4. Run a quick Resume Griller session to ensure question generation, scoring, and persistence still work.
