from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ScoreBundle:
    resume_score: float
    github_score: float
    combined_score: float
