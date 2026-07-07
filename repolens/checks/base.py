"""The check protocol and a registry of built-in checks."""

from __future__ import annotations

from collections.abc import Callable

from ..discovery import Repo
from ..models import Finding

# A check is just a function from a repo to a finding. Keeping it a plain
# callable (rather than a class hierarchy) makes checks trivial to write and
# to unit test.
Check = Callable[[Repo], Finding]

_REGISTRY: list[Check] = []


def register(func: Check) -> Check:
    """Decorator that adds a check to the default suite."""
    _REGISTRY.append(func)
    return func


def all_checks() -> list[Check]:
    """Return the registered checks, importing the modules that define them."""
    # Imported here to avoid a circular import at module load time.
    from . import (  # noqa: F401
        ci,
        documentation,
        licensing,
        packaging,
        security,
        testing,
    )

    return list(_REGISTRY)


def finding(
    repo_check: str,
    title: str,
    category: str,
    *,
    weight: int,
    passed: bool | None,
    message: str,
    partial: float | None = None,
    remediation: str | None = None,
) -> Finding:
    """Build a :class:`Finding`, translating a pass/warn/fail into a score.

    ``passed=True`` awards full weight, ``False`` awards nothing, and
    ``None`` marks a warning worth ``partial`` (defaulting to half credit).
    """
    from ..models import Status

    if passed is True:
        status, earned = Status.PASS, float(weight)
    elif passed is False:
        status, earned = Status.FAIL, 0.0
    else:
        share = 0.5 if partial is None else partial
        status, earned = Status.WARN, round(weight * share, 2)

    return Finding(
        id=repo_check,
        title=title,
        category=category,
        status=status,
        weight=weight,
        earned=earned,
        message=message,
        remediation=remediation if status is not Status.PASS else None,
    )
