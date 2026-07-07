"""Continuous-integration checks."""

from __future__ import annotations

from ..discovery import Repo
from ..models import Finding
from .base import finding, register

CATEGORY = "CI/CD"

# Common CI configuration locations across providers.
_CI_GLOBS = (
    ".github/workflows/*.yml",
    ".github/workflows/*.yaml",
    ".gitlab-ci.yml",
    ".circleci/config.yml",
    "azure-pipelines.yml",
    ".drone.yml",
    "Jenkinsfile",
)


@register
def ci_configured(repo: Repo) -> Finding:
    found: list[str] = []
    for pattern in _CI_GLOBS:
        found.extend(repo.glob(pattern))
    return finding(
        "ci.configured",
        "Continuous integration",
        CATEGORY,
        weight=12,
        passed=bool(found),
        message=(
            f"{len(found)} CI config file(s) detected" if found else "no CI configuration found"
        ),
        remediation=(
            "Add a CI workflow (e.g. .github/workflows/ci.yml) that lints and "
            "tests every push and pull request."
        ),
    )
