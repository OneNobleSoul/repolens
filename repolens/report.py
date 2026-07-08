"""Render a :class:`Report` as text, JSON or Markdown."""

from __future__ import annotations

import json
from collections import defaultdict

from .colors import Palette
from .models import Report, Status

_STATUS_STYLE = {
    Status.PASS: ("green",),
    Status.WARN: ("yellow",),
    Status.FAIL: ("red",),
    Status.SKIP: ("grey",),
}


def render_text(report: Report, palette: Palette) -> str:
    lines: list[str] = []
    lines.append(palette(f"repolens · {report.path}", "bold"))
    lines.append("")

    by_category: dict[str, list] = defaultdict(list)
    for f in report.findings:
        by_category[f.category].append(f)

    for category in sorted(by_category):
        lines.append(palette(category, "bold", "cyan"))
        for f in by_category[category]:
            icon = palette(f.status.icon, *_STATUS_STYLE[f.status])
            head = f"  {icon} {f.title}"
            detail = palette(f"— {f.message}", "dim")
            lines.append(f"{head}  {detail}")
            if f.remediation:
                lines.append(palette(f"      ↳ {f.remediation}", "grey"))
        lines.append("")

    lines.append(_render_summary(report, palette))
    return "\n".join(lines)


def _render_summary(report: Report, palette: Palette) -> str:
    score = report.score
    if score >= 90:
        style = ("green", "bold")
    elif score >= 70:
        style = ("yellow", "bold")
    else:
        style = ("red", "bold")

    bar = _score_bar(score)
    counts = report.counts()
    tally = (
        f"{counts['pass']} passed · {counts['warn']} warnings · "
        f"{counts['fail']} failed"
    )
    headline = palette(f"Score {score:.0f}/100  ({report.grade})", *style)
    return f"{headline}\n{palette(bar, *style)}\n{palette(tally, 'dim')}"


def _score_bar(score: float, width: int = 30) -> str:
    filled = round(score / 100 * width)
    return "▐" + "█" * filled + "░" * (width - filled) + "▌"


def render_json(report: Report) -> str:
    return json.dumps(report.to_dict(), indent=2, ensure_ascii=False)


def render_markdown(report: Report) -> str:
    lines: list[str] = []
    lines.append(f"## repolens report — {report.grade} ({report.score:.0f}/100)")
    lines.append("")
    counts = report.counts()
    lines.append(
        f"**{counts['pass']} passed · {counts['warn']} warnings · "
        f"{counts['fail']} failed**"
    )
    lines.append("")
    lines.append("| Category | Check | Status | Notes |")
    lines.append("| --- | --- | --- | --- |")

    emoji = {
        Status.PASS: "✅",
        Status.WARN: "⚠️",
        Status.FAIL: "❌",
        Status.SKIP: "⏭️",
    }
    for f in report.findings:
        note = f.message.replace("|", "\\|")
        lines.append(
            f"| {f.category} | {f.title} | {emoji[f.status]} | {note} |"
        )

    remediations = [f for f in report.findings if f.remediation]
    if remediations:
        lines.append("")
        lines.append("### Suggested fixes")
        for f in remediations:
            lines.append(f"- **{f.title}** — {f.remediation}")

    return "\n".join(lines)
