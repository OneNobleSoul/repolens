"""Core data types shared across checks and reporting."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class Status(StrEnum):
    """Outcome of a single check.

    A ``StrEnum`` so results serialise cleanly to JSON without a custom
    encoder.
    """

    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"
    SKIP = "skip"

    @property
    def icon(self) -> str:
        return {
            Status.PASS: "✔",
            Status.WARN: "▲",
            Status.FAIL: "✗",
            Status.SKIP: "–",
        }[self]


@dataclass(slots=True)
class Finding:
    """The result of running one check against a repository."""

    id: str
    title: str
    category: str
    status: Status
    weight: int
    earned: float
    message: str
    remediation: str | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "status": self.status.value,
            "weight": self.weight,
            "earned": round(self.earned, 2),
            "message": self.message,
            "remediation": self.remediation,
        }


@dataclass(slots=True)
class Report:
    """Aggregate result of an audit run."""

    path: str
    findings: list[Finding] = field(default_factory=list)

    @property
    def scored(self) -> list[Finding]:
        """Findings that count toward the score (everything but skips)."""
        return [f for f in self.findings if f.status is not Status.SKIP]

    @property
    def total_weight(self) -> int:
        return sum(f.weight for f in self.scored)

    @property
    def total_earned(self) -> float:
        return sum(f.earned for f in self.scored)

    @property
    def score(self) -> float:
        """Overall score from 0 to 100."""
        if self.total_weight == 0:
            return 0.0
        return round(self.total_earned / self.total_weight * 100, 1)

    @property
    def grade(self) -> str:
        return grade_for(self.score)

    def counts(self) -> dict[str, int]:
        out = {s.value: 0 for s in Status}
        for f in self.findings:
            out[f.status.value] += 1
        return out

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "score": self.score,
            "grade": self.grade,
            "counts": self.counts(),
            "findings": [f.to_dict() for f in self.findings],
        }


def grade_for(score: float) -> str:
    """Map a 0–100 score onto a letter grade."""
    thresholds = [
        (95, "A+"),
        (90, "A"),
        (80, "B"),
        (70, "C"),
        (60, "D"),
    ]
    for cutoff, letter in thresholds:
        if score >= cutoff:
            return letter
    return "F"
