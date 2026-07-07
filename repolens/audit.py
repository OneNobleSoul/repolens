"""Run the check suite against a repository and collect the results."""

from __future__ import annotations

from .checks.base import Check, all_checks
from .discovery import Repo
from .models import Finding, Report, Status


def audit(path: str, checks: list[Check] | None = None) -> Report:
    """Audit the repository at ``path`` and return a :class:`Report`.

    Convenience wrapper that builds a :class:`Repo` from a path. Library
    callers that already hold a :class:`Repo` can use :func:`audit_repo`.
    """
    return audit_repo(Repo(path), checks)


def audit_repo(repo: Repo, checks: list[Check] | None = None) -> Report:
    """Audit an already-constructed :class:`Repo`.

    A check that raises is not allowed to abort the whole run; it is
    recorded as a skipped finding so one buggy rule can't hide the rest.
    """
    suite = checks if checks is not None else all_checks()

    report = Report(path=str(repo.root))
    for check in suite:
        try:
            report.findings.append(check(repo))
        except Exception as exc:  # noqa: BLE001 - defensive by design
            report.findings.append(
                Finding(
                    id=getattr(check, "__name__", "unknown"),
                    title=getattr(check, "__name__", "unknown check"),
                    category="Internal",
                    status=Status.SKIP,
                    weight=0,
                    earned=0.0,
                    message=f"check raised {type(exc).__name__}: {exc}",
                )
            )

    report.findings.sort(key=lambda f: (f.category, f.id))
    return report
