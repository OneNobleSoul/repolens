"""Checks about how discoverable and understandable a project is."""

from __future__ import annotations

import re

from ..discovery import Repo
from ..models import Finding
from .base import finding, register

CATEGORY = "Documentation"

_README_NAMES = ("README.md", "README.rst", "README.txt", "README")
_SECTION_HINTS = (
    "install",
    "usage",
    "getting started",
    "quick start",
    "example",
)


@register
def readme_present(repo: Repo) -> Finding:
    name = repo.find_root(*_README_NAMES)
    return finding(
        "readme.present",
        "README file",
        CATEGORY,
        weight=12,
        passed=name is not None,
        message=f"found {name}" if name else "no README at the repository root",
        remediation="Add a README that explains what the project does and how to use it.",
    )


@register
def readme_quality(repo: Repo) -> Finding:
    name = repo.find_root(*_README_NAMES)
    if name is None:
        return finding(
            "readme.quality",
            "README depth",
            CATEGORY,
            weight=8,
            passed=False,
            message="no README to evaluate",
            remediation="Add a README covering installation and usage.",
        )

    text = repo.read(name)
    lowered = text.lower()
    hits = [h for h in _SECTION_HINTS if h in lowered]
    has_headings = bool(re.search(r"^#{1,6}\s", text, re.MULTILINE))
    long_enough = len(text) >= 600

    if long_enough and has_headings and hits:
        return finding(
            "readme.quality",
            "README depth",
            CATEGORY,
            weight=8,
            passed=True,
            message=f"structured README ({len(text)} chars, sections: {', '.join(hits)})",
        )

    missing = []
    if not long_enough:
        missing.append("more detail")
    if not has_headings:
        missing.append("section headings")
    if not hits:
        missing.append("install/usage guidance")
    return finding(
        "readme.quality",
        "README depth",
        CATEGORY,
        weight=8,
        passed=None,
        message="README is thin: " + ", ".join(missing),
        remediation="Expand the README with headings and an installation/usage section.",
    )


@register
def changelog(repo: Repo) -> Finding:
    name = repo.find_root("CHANGELOG.md", "CHANGELOG.rst", "CHANGELOG", "HISTORY.md")
    return finding(
        "docs.changelog",
        "Changelog",
        CATEGORY,
        weight=5,
        passed=name is not None,
        message=f"found {name}" if name else "no changelog",
        remediation="Keep a CHANGELOG.md so users can see what changed between releases.",
    )


@register
def contributing(repo: Repo) -> Finding:
    name = repo.find_root("CONTRIBUTING.md", "CONTRIBUTING.rst", "CONTRIBUTING")
    if name is None:
        name = next(iter(repo.glob(".github/CONTRIBUTING*")), None)
    return finding(
        "docs.contributing",
        "Contribution guide",
        CATEGORY,
        weight=6,
        passed=name is not None,
        message=f"found {name}" if name else "no contribution guide",
        remediation="Add CONTRIBUTING.md so newcomers know how to help.",
    )


@register
def code_of_conduct(repo: Repo) -> Finding:
    name = repo.find_root("CODE_OF_CONDUCT.md", "CODE_OF_CONDUCT")
    if name is None:
        name = next(iter(repo.glob(".github/CODE_OF_CONDUCT*")), None)
    return finding(
        "docs.code_of_conduct",
        "Code of conduct",
        CATEGORY,
        weight=4,
        passed=name is not None,
        message=f"found {name}" if name else "no code of conduct",
        remediation="Adopt a code of conduct (the Contributor Covenant is a common choice).",
    )
