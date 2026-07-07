"""Licensing check — arguably the single most important file in a repo."""

from __future__ import annotations

from ..discovery import Repo
from ..models import Finding
from .base import finding, register

CATEGORY = "Licensing"

_LICENSE_NAMES = (
    "LICENSE",
    "LICENSE.md",
    "LICENSE.txt",
    "LICENCE",
    "LICENCE.md",
    "COPYING",
    "COPYING.md",
)


@register
def license_present(repo: Repo) -> Finding:
    name = repo.find_root(*_LICENSE_NAMES)
    if name is None:
        name = next(iter(repo.glob(".github/LICENSE*")), None)
    return finding(
        "license.present",
        "License",
        CATEGORY,
        weight=12,
        passed=name is not None,
        message=f"found {name}" if name else "no license file",
        remediation=(
            "Add a LICENSE file. Without one the code is 'all rights reserved' "
            "and nobody can legally reuse it."
        ),
    )
