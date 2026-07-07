"""Filesystem access for a repository under audit.

The :class:`Repo` object is the single place that knows how to look at a
project on disk. Checks receive one and ask questions like "is there a
README?" or "give me the tracked text files" without touching the
filesystem directly. That keeps checks small and easy to test with a
temporary directory.
"""

from __future__ import annotations

import fnmatch
import os
import subprocess
from functools import cached_property
from pathlib import Path

# Directories we never want to walk into when git is unavailable.
_PRUNE = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    "dist",
    "build",
    ".tox",
    ".idea",
    "target",
}

# Only read text files up to this size when scanning contents.
_MAX_SCAN_BYTES = 512_000


class Repo:
    """A project directory to inspect."""

    def __init__(self, root: str | os.PathLike[str]) -> None:
        self.root = Path(root).resolve()
        if not self.root.is_dir():
            raise NotADirectoryError(f"not a directory: {self.root}")

    # -- basic facts ------------------------------------------------------

    @cached_property
    def config(self):
        from .config import load

        return load(self.root)

    @cached_property
    def is_git_repo(self) -> bool:
        return (self.root / ".git").exists()

    @cached_property
    def files(self) -> list[str]:
        """Relative paths of files in the project.

        Prefers ``git ls-files`` so we honour ``.gitignore`` and only look
        at what is actually committed. Falls back to a pruned filesystem
        walk for non-git projects.
        """
        tracked = self._git_tracked_files()
        if tracked is not None:
            return tracked
        return self._walk_files()

    def _git_tracked_files(self) -> list[str] | None:
        if not self.is_git_repo:
            return None
        try:
            out = subprocess.run(
                ["git", "ls-files", "-z"],
                cwd=self.root,
                capture_output=True,
                check=True,
                timeout=15,
            )
        except (OSError, subprocess.SubprocessError):
            return None
        entries = out.stdout.decode("utf-8", "replace").split("\0")
        files = [e for e in entries if e]
        # A freshly-initialised repo with nothing committed yet should fall
        # back to a walk rather than reporting an empty project.
        return files or None

    def _walk_files(self) -> list[str]:
        found: list[str] = []
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames[:] = [d for d in dirnames if d not in _PRUNE]
            for name in filenames:
                rel = os.path.relpath(os.path.join(dirpath, name), self.root)
                found.append(rel.replace(os.sep, "/"))
        return found

    # -- lookups ----------------------------------------------------------

    def has(self, *names: str) -> bool:
        """True if any of ``names`` exists at the repo root (case-insensitive)."""
        return self.find_root(*names) is not None

    def find_root(self, *names: str) -> str | None:
        """Return the first matching top-level file, ignoring case."""
        wanted = {n.lower() for n in names}
        for rel in self.files:
            if "/" in rel:
                continue
            if rel.lower() in wanted:
                return rel
        return None

    def glob(self, pattern: str) -> list[str]:
        """Return tracked files matching a glob pattern (case-insensitive).

        ``fnmatch``'s ``*`` already spans path separators, so ``a/*`` matches
        anything under ``a/``. A leading ``**/`` additionally matches the
        pattern against the bare filename so ``**/test_*.py`` also catches
        top-level ``test_foo.py``.
        """
        pat = pattern.lower()
        base_pat = pat[3:] if pat.startswith("**/") else None
        out: list[str] = []
        for f in self.files:
            fl = f.lower()
            if fnmatch.fnmatch(fl, pat) or (
                base_pat is not None
                and (
                    fnmatch.fnmatch(fl, base_pat)
                    or fnmatch.fnmatch(fl.rsplit("/", 1)[-1], base_pat)
                )
            ):
                out.append(f)
        return out

    def read(self, rel: str) -> str:
        return (self.root / rel).read_text(encoding="utf-8", errors="replace")

    def iter_text_files(self):
        """Yield ``(relpath, content)`` for reasonably-sized text files."""
        for rel in self.files:
            path = self.root / rel
            try:
                if path.stat().st_size > _MAX_SCAN_BYTES:
                    continue
                data = path.read_bytes()
            except OSError:
                continue
            if b"\0" in data:  # crude but effective binary sniff
                continue
            yield rel, data.decode("utf-8", "replace")
