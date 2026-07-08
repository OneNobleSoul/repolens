"""Optional per-project configuration.

Configuration is read from ``.repolens.toml`` at the repository root, or from
a ``[tool.repolens]`` table in ``pyproject.toml``. Everything is optional —
repolens works with zero configuration.

Example ``.repolens.toml``::

    min_score = 80

    [secrets]
    ignore = ["tests/**", "docs/examples/*"]
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class Config:
    min_score: float | None = None
    secret_ignore: list[str] = field(default_factory=list)


def load(root: Path) -> Config:
    """Load configuration for the repo at ``root`` (never raises on bad input)."""
    data = _read_repolens_toml(root)
    if data is None:
        data = _read_pyproject(root)
    if not data:
        return Config()

    secrets = data.get("secrets", {})
    ignore = secrets.get("ignore", []) if isinstance(secrets, dict) else []

    min_score = data.get("min_score")
    if not isinstance(min_score, (int, float)):
        min_score = None

    return Config(
        min_score=float(min_score) if min_score is not None else None,
        secret_ignore=[str(x) for x in ignore] if isinstance(ignore, list) else [],
    )


def _read_repolens_toml(root: Path) -> dict | None:
    path = root / ".repolens.toml"
    if not path.is_file():
        return None
    return _parse(path)


def _read_pyproject(root: Path) -> dict | None:
    path = root / "pyproject.toml"
    if not path.is_file():
        return None
    parsed = _parse(path)
    if not parsed:
        return None
    tool = parsed.get("tool", {})
    if isinstance(tool, dict) and isinstance(tool.get("repolens"), dict):
        return tool["repolens"]
    return None


def _parse(path: Path) -> dict | None:
    try:
        with path.open("rb") as fh:
            return tomllib.load(fh)
    except (OSError, tomllib.TOMLDecodeError):
        return None
