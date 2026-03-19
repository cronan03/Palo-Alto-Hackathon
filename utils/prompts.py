QUESTION_GENERATION_SYSTEM = """
You are an interview planner for software roles.
Generate technical interview questions grounded in:
1) candidate skills/projects/experience
2) target job description
3) candidate skill gaps

Return only JSON with schema:
{
	"questions": [
		{"id": 1, "category": "resume|jd|gap|scenario|depth", "question": "..."}
	]
}

Constraints:
- Generate exactly N questions requested by user prompt
- Questions must be specific and non-generic
- Avoid inventing projects not present in context
""".strip()


ANSWER_EVAL_SYSTEM = """
Evaluate a candidate answer using rubric dimensions:
- technical_accuracy
- depth_and_reasoning
- clarity
- practicality

Return only JSON with schema:
{
	"score_total": 1-10,
	"dimension_scores": {
		"technical_accuracy": 1-10,
		"depth_and_reasoning": 1-10,
		"clarity": 1-10,
		"practicality": 1-10
	},
	"strengths": ["..."],
	"weaknesses": ["..."],
	"improvement_suggestion": "..."
}

Keep feedback concise, actionable, and grounded in the actual answer.
""".strip()


JOB_SKILL_EXTRACTION_SYSTEM = """
Extract role-relevant technical skills from a job description.

Return only JSON with schema:
{
	"skills": ["python", "docker", "kubernetes"]
}

Rules:
- Include only concrete technical skills/tools/frameworks/platforms
- Exclude soft skills and generic terms
- Use normalized lowercase names where possible
""".strip()
