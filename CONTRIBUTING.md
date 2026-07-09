# Contributing to repolens

Thanks for taking the time to help out. This project is small on purpose, so
contributing is meant to be low-ceremony.

## Getting set up

```bash
git clone https://github.com/UnterwegsDev/repolens
cd repolens
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

Run the checks that CI runs:

```bash
ruff check .
pytest
```

repolens also audits itself — a nice sanity check before opening a PR:

```bash
python -m repolens . --min-score 90
```

## Adding a check

A check is a function that takes a `Repo` and returns a `Finding`. The
`finding()` helper turns a pass/warn/fail into a weighted score for you.

```python
# repolens/checks/documentation.py
from ..discovery import Repo
from ..models import Finding
from .base import finding, register


@register
def citation_file(repo: Repo) -> Finding:
    name = repo.find_root("CITATION.cff")
    return finding(
        "docs.citation",
        "Citation metadata",
        "Documentation",
        weight=3,
        passed=name is not None,
        message=f"found {name}" if name else "no CITATION.cff",
        remediation="Add a CITATION.cff so people can cite your work.",
    )
```

The `@register` decorator adds it to the default suite. Then add a test in
`tests/test_checks.py` using the `make_repo` fixture, which builds a throwaway
repo from a `{path: content}` mapping.

## Guidelines

- Keep checks **high-signal**. A check that fires on healthy repos is worse
  than no check at all — the secret scanner, for example, favours precision
  over recall on purpose.
- Every non-passing finding should carry an actionable `remediation`.
- New behaviour comes with a test. `pytest` should stay green and fast.
- Formatting and linting are handled by `ruff`; run `ruff check --fix .`
  before pushing.

## Reporting bugs & ideas

Open an issue using one of the templates. For security-sensitive reports,
please follow [SECURITY.md](SECURITY.md) instead of filing a public issue.
