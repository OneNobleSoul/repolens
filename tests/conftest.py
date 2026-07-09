"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from repolens.discovery import Repo


@pytest.fixture
def make_repo(tmp_path: Path):
    """Return a factory that materialises a repo from a ``{path: content}`` map."""

    def _make(files: dict[str, str]) -> Repo:
        for rel, content in files.items():
            target = tmp_path / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        return Repo(tmp_path)

    return _make
