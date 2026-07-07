"""Tiny ANSI colour helper with sensible auto-detection.

No dependencies on purpose — a health-check tool that pulls in a rendering
library for four escape codes would be failing its own audit.
"""

from __future__ import annotations

import os
import sys

_CODES = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "cyan": "\033[36m",
    "grey": "\033[90m",
}


class Palette:
    """Wraps text in ANSI codes, or not, depending on ``enabled``."""

    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled

    def __call__(self, text: str, *styles: str) -> str:
        if not self.enabled or not styles:
            return text
        prefix = "".join(_CODES[s] for s in styles if s in _CODES)
        return f"{prefix}{text}{_CODES['reset']}"


def should_color(stream=sys.stdout, force: bool | None = None) -> bool:
    """Decide whether colour output is appropriate.

    Honours the widely-supported ``NO_COLOR`` and ``FORCE_COLOR`` env vars
    before falling back to a TTY check.
    """
    if force is not None:
        return force
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    return bool(getattr(stream, "isatty", lambda: False)())
