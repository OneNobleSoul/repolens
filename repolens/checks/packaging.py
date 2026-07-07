"""Does the project declare how it is built and distributed?"""

from __future__ import annotations

from ..discovery import Repo
from ..models import Finding
from .base import finding, register

CATEGORY = "Packaging"

_MANIFESTS = (
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "package.json",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "composer.json",
    "Gemfile",
)

_EDITORCONFIG = (".editorconfig",)


@register
def manifest_present(repo: Repo) -> Finding:
    name = repo.find_root(*_MANIFESTS)
    return finding(
        "packaging.manifest",
        "Package manifest",
        CATEGORY,
        weight=6,
        passed=name is not None,
        message=f"found {name}" if name else "no build/package manifest",
        remediation=(
            "Add a manifest (pyproject.toml, package.json, Cargo.toml, …) so the "
            "project can be built and installed reproducibly."
        ),
    )


@register
def editorconfig(repo: Repo) -> Finding:
    name = repo.find_root(*_EDITORCONFIG)
    return finding(
        "packaging.editorconfig",
        "Editor configuration",
        CATEGORY,
        weight=2,
        passed=name is not None,
        message="found .editorconfig" if name else "no .editorconfig",
        remediation="Add an .editorconfig to keep indentation consistent across editors.",
    )
