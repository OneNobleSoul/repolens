"""Does the project ship automated tests?"""

from __future__ import annotations

from ..discovery import Repo
from ..models import Finding
from .base import finding, register

CATEGORY = "Testing"

_TEST_GLOBS = (
    "test/*",
    "tests/*",
    "spec/*",
    "**/test_*.py",
    "**/*_test.py",
    "**/*_test.go",
    "**/*.test.js",
    "**/*.test.ts",
    "**/*.spec.js",
    "**/*.spec.ts",
    "**/*test*.rs",
)


@register
def tests_present(repo: Repo) -> Finding:
    matches: set[str] = set()
    for pattern in _TEST_GLOBS:
        matches.update(repo.glob(pattern))
    # A lone config file inside tests/ shouldn't count; require a real file.
    count = len([m for m in matches if not m.endswith("/")])
    return finding(
        "testing.present",
        "Automated tests",
        CATEGORY,
        weight=10,
        passed=count > 0,
        message=f"{count} test file(s) found" if count else "no test files detected",
        remediation=(
            "Add a tests/ directory with unit tests so regressions get caught "
            "before release."
        ),
    )
