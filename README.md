# Skill-Bridge Career Navigator (MVP In Progress)

## What is implemented now
- Streamlit multi-page app shell
- Home onboarding with resume upload and GitHub username
- Resume parsing baseline (skills, projects, experience)
- GitHub parsing baseline (repos, inferred skills, score)
- Unified weighted score (0.6 GitHub + 0.4 Resume)
- Dashboard with score cards and skill chart
- Job Match with missing skills, gap clusters, recommendations, and knowledge graph
- Leaderboard by college with filters and histogram
- Resume Griller basic interview flow with per-answer feedback and final summary
- SQLite persistence for:
  - Users
  - Job match runs
  - Interview runs

## Project structure
- app/main.py
- app/pages/1_Home.py
- app/pages/2_Dashboard.py
- app/pages/3_Job_Match.py
- app/pages/4_Leaderboard.py
- app/pages/5_Resume_Griller.py
- core/
- utils/
- storage/
- data/
- tests/

## Setup
1. Create virtual environment
2. Install dependencies
3. Configure Gemini API key
4. Run Streamlit app

### Commands (PowerShell)
```powershell
cd hack
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app/main.py
```

## LLM configuration (Gemini)
1. Copy .env.example to .env
2. Set GEMINI_API_KEY in .env
3. Optionally change GEMINI_MODEL (default is gemini-1.5-flash)

Example .env:
```env
GEMINI_API_KEY=your_real_key
GEMINI_MODEL=gemini-1.5-flash
```

Behavior:
- If GEMINI_API_KEY is present, Job Match skill extraction and Resume Griller Q/A evaluation use Gemini.
- If key is missing or API response is invalid, the app automatically falls back to local heuristic logic.

## Next implementation steps
1. Replace heuristic JD skill extraction with LLM + embedding matcher
2. Add GitHub README/content analysis for stronger inferred skill confidence
3. Add interview history and job-match history pages
4. Add authentication and per-user profiles
5. Add unit tests for core engines (resume, github, gap, interview)

## Notes
- Current parsing and interview evaluation are baseline heuristics for MVP speed.
- Gemini-based LLM support is integrated with safe fallback.
