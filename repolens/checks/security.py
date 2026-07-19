"""Security-hygiene checks: policy, ignore rules, dependency updates, secrets."""

from __future__ import annotations

import fnmatch
import re

from ..discovery import Repo
from ..models import Finding
from .base import finding, register

CATEGORY = "Security"

# High-precision patterns. The goal is zero false positives on a normal repo,
# because a noisy secret scanner gets ignored. We would rather miss an exotic
# credential than cry wolf on every base64 string.
_SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("AWS access key id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private key block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |)PRIVATE KEY-----")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{10,}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[0-9A-Za-z]{36}\b")),
    ("GitHub fine-grained token", re.compile(r"\bgithub_pat_[0-9A-Za-z]{22}_[0-9A-Za-z]{59}\b")),
    ("Anthropic API key", re.compile(r"\bsk-ant-(?:api03|oat01)-[0-9A-Za-z_-]{90,}\b")),
    # Modern OpenAI keys embed the base64 literal "OpenAI" (T3BlbkFJ) mid-token,
    # which makes them just as identifiable as the AWS/Google prefixes above.
    (
        "OpenAI API key",
        re.compile(r"\bsk-(?:proj|svcacct|admin)-[0-9A-Za-z_-]{20,}T3BlbkFJ[0-9A-Za-z_-]{20,}\b"),
    ),
    # Only the "live" prefix is flagged — Stripe's "test" keys only work
    # against the sandbox, so they turn up harmlessly in fixtures and docs.
    ("Stripe live API key", re.compile(r"\b(?:sk|rk)_live_[0-9A-Za-z]{24,247}\b")),
    # Fine-grained npm access tokens (introduced 2023) use this fixed-width
    # prefixed format, unlike the legacy plain-UUID tokens, which are too
    # generic to flag without false positives.
    ("npm access token", re.compile(r"\bnpm_[0-9A-Za-z]{36}\b")),
    ("generic private key file", re.compile(r"PRIVATE KEY-----")),
)

# Files we skip when scanning: our own source (which literally contains the
# patterns above) and lockfiles full of hashes.
_SCAN_SKIP = re.compile(
    r"(?:^|/)(?:checks/security\.py|.*\.lock|package-lock\.json|poetry\.lock)$"
)


@register
def security_policy(repo: Repo) -> Finding:
    name = repo.find_root("SECURITY.md", "SECURITY")
    if name is None:
        name = next(iter(repo.glob(".github/SECURITY*")), None)
    return finding(
        "security.policy",
        "Security policy",
        CATEGORY,
        weight=6,
        passed=name is not None,
        message=f"found {name}" if name else "no SECURITY policy",
        remediation="Add SECURITY.md describing how to report a vulnerability privately.",
    )


@register
def gitignore(repo: Repo) -> Finding:
    name = repo.find_root(".gitignore")
    return finding(
        "security.gitignore",
        "Ignore rules",
        CATEGORY,
        weight=5,
        passed=name is not None,
        message="found .gitignore" if name else "no .gitignore",
        remediation="Add a .gitignore so build output and secrets don't get committed by accident.",
    )


@register
def dependency_updates(repo: Repo) -> Finding:
    found = (
        repo.glob(".github/dependabot.yml")
        or repo.glob(".github/dependabot.yaml")
        or repo.glob(".github/renovate.json")
        or repo.glob("renovate.json")
    )
    return finding(
        "security.dependency_updates",
        "Automated dependency updates",
        CATEGORY,
        weight=5,
        passed=bool(found),
        message="dependency automation configured" if found else "no Dependabot/Renovate config",
        remediation=(
            "Enable Dependabot (.github/dependabot.yml) or Renovate to keep "
            "dependencies patched automatically."
        ),
    )


@register
def committed_secrets(repo: Repo) -> Finding:
    # An accidentally committed .env is a common and serious leak.
    env_committed = [
        f for f in repo.files if f == ".env" or f.endswith("/.env")
    ]

    ignore_globs = repo.config.secret_ignore

    def _ignored(path: str) -> bool:
        return any(
            fnmatch.fnmatch(path, g) or fnmatch.fnmatch(path.rsplit("/", 1)[-1], g)
            for g in ignore_globs
        )

    hits: list[str] = []
    for rel, content in repo.iter_text_files():
        if _SCAN_SKIP.search(rel) or _ignored(rel):
            continue
        for label, pattern in _SECRET_PATTERNS:
            if pattern.search(content):
                hits.append(f"{rel}: {label}")
                break

    if not hits and not env_committed:
        return finding(
            "security.secrets",
            "No committed secrets",
            CATEGORY,
            weight=8,
            passed=True,
            message="no obvious credentials found in tracked files",
        )

    problems = []
    if env_committed:
        problems.append(f"committed env file: {', '.join(env_committed)}")
    problems.extend(hits[:5])
    return finding(
        "security.secrets",
        "No committed secrets",
        CATEGORY,
        weight=8,
        passed=False,
        message="potential secrets detected — " + "; ".join(problems),
        remediation=(
            "Remove the secret, rotate it immediately, and add the path to "
            ".gitignore. Committed credentials must be treated as compromised."
        ),
    )
