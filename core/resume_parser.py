from __future__ import annotations

import re
from typing import BinaryIO

from pypdf import PdfReader

from utils.normalizers import normalize_skills


DEFAULT_SKILL_BANK = {
    "python",
    "java",
    "javascript",
    "typescript",
    "sql",
    "docker",
    "kubernetes",
    "aws",
    "gcp",
    "azure",
    "react",
    "nodejs",
    "fastapi",
    "flask",
    "django",
    "pandas",
    "numpy",
    "machine learning",
    "tensorflow",
    "pytorch",
    "git",
    "ci/cd",
}


def extract_text(pdf_file: BinaryIO) -> str:
    """Extract plain text from a PDF file-like object."""
    try:
        reader = PdfReader(pdf_file)
        chunks = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(chunks).strip()
    except Exception:
        return ""


def extract_skills(text: str) -> list[str]:
    lowered = text.lower()
    found = [skill for skill in DEFAULT_SKILL_BANK if re.search(rf"\b{re.escape(skill)}\b", lowered)]
    return normalize_skills(found)


def extract_projects(text: str) -> list[str]:
    project_lines = []
    for line in text.splitlines():
        if any(tok in line.lower() for tok in ["project", "built", "developed", "designed"]):
            cleaned = line.strip(" -\t")
            if cleaned:
                project_lines.append(cleaned)
    # Keep a reasonable cap so the dashboard remains readable,
    # but allow more projects to surface than before.
    return project_lines[:20]


def extract_experience(text: str) -> dict:
    years_matches = re.findall(r"(\d+)\+?\s+years", text.lower())
    years = max([int(y) for y in years_matches], default=0)
    experience_lines = []
    leadership_lines = []

    leadership_prefixes = ("Spearheaded", "Instructed", "Directed")

    for raw in text.splitlines():
        line = raw.strip(" -\t•")
        lowered = line.lower()
        if not line:
            continue

        if any(tok in lowered for tok in ["intern", "engineer", "developer", "experience", "analyst", "research", "manager", "architect"]):
            experience_lines.append(line)

        if line.startswith(leadership_prefixes):
            leadership_lines.append(line)

    return {
        "years": years,
        "has_internship": "intern" in text.lower(),
        "highlights": experience_lines[:20],
        "leadership": leadership_lines[:20],
    }
