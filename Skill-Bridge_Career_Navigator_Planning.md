# Skill-Bridge Career Navigator

## 1) Product Summary
Skill-Bridge Career Navigator is an AI-powered Streamlit web app that helps students and early-career professionals:
- Parse resume claims
- Analyze demonstrated GitHub skills
- Compute a unified skill profile
- Identify job-role skill gaps
- Practice interviews using a Resume Griller
- Benchmark against peers via college leaderboard

## 2) Problem Statement
Candidates often do not know:
- Which skills they truly demonstrate
- How close they are to a target role
- What to improve first
- How they compare with peers

Recruiters and career mentors need an objective, explainable readiness signal.

## 3) Goals and Non-Goals
### Goals (MVP)
- Resume PDF parsing and structured extraction
- GitHub profile analysis for inferred skills
- Unified weighted score and skill confidence profile
- Job match and skill gap analysis from JD text
- College-level leaderboard
- Resume Griller with 5-7 Q&A rounds and feedback

### Non-Goals (MVP)
- Real-time collaboration
- Deep anti-cheat plagiarism detection
- Full ATS integration
- Voice interview mode

## 4) Users and Personas
- Student (primary): wants clear next steps to become job-ready
- Early-career professional: wants role transition guidance
- College placement coordinator: wants cohort benchmarking

## 5) High-Level Architecture
User Input (Resume + GitHub + College + Optional Metadata)
-> Parsing Layer (Resume Parser, GitHub Analyzer)
-> Unified Skill Profile
-> Scoring and Gap Analysis Engines
-> Interview Engine (Resume Griller)
-> Streamlit Multi-Page UI
-> Persistence Layer (SQLite/Postgres for production)

## 6) Technical Stack
- Frontend: Streamlit (multi-page)
- Backend app layer: Python modules
- NLP/LLM: OpenAI-compatible API or local LLM fallback
- Embeddings: sentence-transformers (MVP) or OpenAI embeddings
- Graph: networkx + pyvis
- Storage:
  - MVP: Streamlit session_state + SQLite
  - Production: Postgres + Redis cache
- Data ingestion:
  - Resume: pdfplumber / pypdf
  - GitHub: GitHub REST API (plus optional GraphQL)

## 7) Core Modules and Responsibilities
### 7.1 Resume Processing Module
Functions:
- extract_text(pdf_file) -> str
- extract_sections(text) -> dict
- extract_skills(text) -> list[str]
- extract_projects(text) -> list[dict]
- extract_experience(text) -> dict
- normalize_skills(skills) -> list[str]

Notes:
- Use regex + heuristics first, then LLM structured parse for robustness
- Keep raw text and parsed JSON for traceability

### 7.2 GitHub Processing Module
Functions:
- get_user_profile(username) -> dict
- get_repos(username) -> list[dict]
- analyze_repo(repo) -> dict
- infer_skills(repo_bundle) -> dict[str, float]
- compute_github_score(metrics) -> float

Signals:
- Language usage
- Repo recency and activity
- README technical depth
- Topics/tags
- Stars/forks (light weight in MVP)

### 7.3 Skill Engine
Functions:
- normalize_skill(skill) -> str
- merge_resume_github_skills(resume, github) -> dict
- compute_unified_score(resume_score, github_score) -> float
- confidence_calibration(skill_evidence) -> float

Baseline formula:
- combined_score = 0.6 * github_score + 0.4 * resume_score

Skill confidence idea:
- confidence(skill) = 0.5 * evidence_strength + 0.3 * recency + 0.2 * project_diversity

### 7.4 Gap Analysis Engine
Functions:
- extract_job_skills(jd_text) -> list[str]
- embed_skills(skill_list) -> vectors
- semantic_match(user_skills, job_skills) -> dict
- compute_match_score(matches) -> float
- find_missing_skills(matches, threshold=0.55) -> list[str]
- cluster_missing_skills(missing) -> dict[str, list[str]]

Output:
- match_percentage
- matched_skills
- missing_skills
- clustered_gaps (DevOps, Backend, ML, Data, etc.)

### 7.5 Interview Engine (Resume Griller)
Functions:
- build_interview_context(profile, jd) -> str
- generate_questions(profile, jd, n=5) -> list[dict]
- evaluate_answer(question, answer, rubric) -> dict
- summarize_interview(session_logs) -> dict

Question categories:
- Resume-based
- JD-based
- Gap-based
- Scenario-based

Round constraints:
- 5-7 questions max
- One question at a time
- Structured rubric scoring (1-10)

### 7.6 Leaderboard Engine
Functions:
- compute_rankings(users_df) -> users_df
- college_insights(users_df) -> dict
- filter_rankings(users_df, branch=None, year=None) -> users_df

Score columns:
- resume_score
- github_score
- combined_score

## 8) Proposed Data Model
### 8.1 user_profile
- user_id (uuid)
- name
- college
- branch (optional)
- year (optional)
- github_username
- created_at
- updated_at

### 8.2 resume_artifact
- user_id
- resume_text
- parsed_resume_json
- resume_score

### 8.3 github_artifact
- user_id
- github_metrics_json
- inferred_skills_json
- github_score

### 8.4 unified_skill_profile
- user_id
- skills_json (skill -> confidence)
- combined_score

### 8.5 job_match_run
- run_id
- user_id
- jd_text
- extracted_job_skills_json
- match_score
- missing_skills_json
- created_at

### 8.6 interview_run
- run_id
- user_id
- jd_text
- questions_json
- answers_json
- evaluations_json
- final_summary_json
- created_at

## 9) API/Service Contract (Internal)
- parse_resume_service(pdf) -> ResumeParseResponse
- github_analysis_service(username) -> GitHubAnalysisResponse
- build_skill_profile_service(user_id) -> SkillProfileResponse
- job_match_service(user_id, jd_text) -> JobMatchResponse
- interview_service(user_id, jd_text, answer=None, step=None) -> InterviewStateResponse
- leaderboard_service(college, filters) -> LeaderboardResponse

## 10) Streamlit UI Plan (5 Pages)

### Page 1: Home / Onboarding
Inputs:
- Name
- College
- Branch (optional)
- Year (optional)
- Resume upload (PDF)
- GitHub username

Actions:
- Parse resume
- Fetch and score GitHub profile
- Build unified skill profile
- Persist user data

Output:
- Setup complete confirmation
- CTA to go to dashboard

### Page 2: Resume + GitHub Dashboard
Cards:
- Resume Score
- GitHub Score
- Combined Score

Visuals:
- Skill confidence bar chart
- Radar chart for skill clusters
- Insight callouts (strengths and weak zones)

### Page 3: Job Match + Gap Analysis
Input:
- Job description text area

Processing:
- Extract JD skills
- Semantic match with user profile
- Generate gap clusters and recommendations

Output:
- Match score percentage
- Missing skills list
- Cluster breakdown
- Recommendations list
- Knowledge graph visualization

### Page 4: College Leaderboard
Features:
- Ranking table
- Filters by branch and year
- Score distribution histogram
- Top-performer spotlight
- Cohort insight text summaries

### Page 5: Resume Griller
Sections:
- Interview Start panel
- Live question panel (one question at a time)
- Feedback panel (per answer)
- Final summary report panel

Flow:
- Start interview
- Generate 5-7 contextual questions
- Evaluate each answer with rubric
- Aggregate final score and focus areas

## 11) Prompt Design
### 11.1 Question Generation Prompt
System intent:
- Generate exactly N technical interview questions based on:
  - Candidate profile
  - GitHub projects
  - Job description
- Include category label per question
- Prefer specific, non-generic questions tied to evidence

Output JSON schema:
- questions: [{id, category, question, expected_signals}]

### 11.2 Answer Evaluation Prompt
Rubric dimensions (1-10 each):
- Technical accuracy
- Depth and reasoning
- Practicality
- Clarity and structure

Output JSON schema:
- score_total
- dimension_scores
- strengths
- weaknesses
- improvement_suggestion

Guardrails:
- Avoid hallucinating candidate projects
- Ground feedback in answer content
- Keep feedback actionable and concise

## 12) Scoring Framework
Resume Score (0-100):
- Skill coverage: 35
- Project quality signals: 35
- Experience richness: 30

GitHub Score (0-100):
- Repo quality/depth: 35
- Activity/consistency: 25
- Skill evidence breadth: 30
- Community signals: 10

Combined Score:
- combined = 0.6 * github + 0.4 * resume

Match Score:
- weighted semantic similarity between JD and user skills
- cap confidence when evidence for claimed skill is weak

## 13) Knowledge Graph Design
Nodes:
- UserSkill
- MissingSkill
- JobRole

Edges:
- HAS_SKILL (user -> skill)
- REQUIRES_SKILL (job -> skill)
- RELATED_TO (skill -> skill)
- GAP_FOR (user -> missing skill)

Visual encoding:
- User skills: green
- Missing skills: red
- Job role: blue center node

## 14) Repository Structure (Recommended)
app/
- main.py
- pages/
  - 1_Home.py
  - 2_Dashboard.py
  - 3_Job_Match.py
  - 4_Leaderboard.py
  - 5_Resume_Griller.py
core/
- resume_parser.py
- github_parser.py
- skill_engine.py
- gap_engine.py
- interview_engine.py
- leaderboard_engine.py
utils/
- prompts.py
- schemas.py
- normalizers.py
- graph_viz.py
data/
- skill_taxonomy.json
- seed_users.csv
storage/
- db.py
tests/
- test_resume_parser.py
- test_github_parser.py
- test_skill_engine.py
- test_gap_engine.py
- test_interview_engine.py

## 15) Delivery Plan
### Phase 1 (Week 1)
- Project skeleton + Streamlit multipage setup
- Resume parser baseline
- GitHub parser baseline
- Unified score computation

### Phase 2 (Week 2)
- Dashboard and Job Match pages
- Embedding-based skill matching
- Missing skill clustering
- Knowledge graph MVP

### Phase 3 (Week 3)
- Leaderboard page + filtering
- Resume Griller basic flow
- Evaluation rubric and final report

### Phase 4 (Week 4)
- Hardening, tests, caching, error handling
- Prompt tuning and quality checks
- Deployment prep

## 16) Risks and Mitigations
Risk: Generic interview questions
Mitigation: Force evidence-linked prompts and include project references

Risk: Inconsistent parsing quality
Mitigation: Heuristic parse + LLM structured fallback + confidence flags

Risk: GitHub API rate limits
Mitigation: Caching, token auth, backoff retries

Risk: User fatigue in interview mode
Mitigation: Limit to 5-7 questions and show progress indicator

## 17) Success Criteria
- User can onboard in under 3 minutes
- Job match response generated in under 10 seconds for typical JD
- Interview report produced after 5-7 questions with actionable feedback
- Leaderboard ranks users reproducibly and transparently
- At least 80% of pilot users report clearer improvement priorities

## 18) MVP Acceptance Checklist
- Resume upload and parsing works for common PDF formats
- GitHub analysis returns inferred skills and score
- Combined score appears on dashboard
- JD input returns match score and missing skills
- Knowledge graph renders in app
- Leaderboard table and histogram render with filters
- Resume Griller completes full interview and summary report

## 19) Future Enhancements
- Adaptive interview questioning based on prior answers
- Voice interview simulation
- Mentor mode with customized learning plans
- ATS keyword optimization assistant
- Fine-grained branch/year benchmarking insights
