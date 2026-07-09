# repolens

[![CI](https://github.com/NobleSoul/repolens/actions/workflows/ci.yml/badge.svg)](https://github.com/NobleSoul/repolens/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/repolens.svg)](https://pypi.org/project/repolens/)
[![Python](https://img.shields.io/pypi/pyversions/repolens.svg)](https://pypi.org/project/repolens/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**A health check for your repository.** repolens looks at a project the way a
careful reviewer would — is there a README worth reading, a license, tests, CI,
a security policy? — and turns that into a score you can act on, print in a
review, or enforce in CI.

It has **no runtime dependencies**, installs in a second, and can audit itself.

```
repolens · ~/code/repolens

Documentation
  ✔ README file            — found README.md
  ✔ README depth           — structured README (2.1k chars, sections: install, usage)
  ✔ Changelog              — found CHANGELOG.md
Security
  ✔ No committed secrets   — no obvious credentials found in tracked files
  ✔ Automated dependency updates — dependency automation configured
...

Score 100/100  (A+)
▐██████████████████████████████▌
15 passed · 0 warnings · 0 failed
```

## Why

Publishing a repository is easy. Publishing one that a stranger can trust,
build and contribute to is a checklist most of us half-remember. repolens is
that checklist, automated — so a missing `LICENSE` or an accidentally committed
`.env` gets caught before it ships, not after.

Think of it as a linter, but for the *project* rather than the *code*.

## Install

```bash
pip install repolens
```

Or run it once without installing:

```bash
pipx run repolens
```

Requires Python 3.11 or newer.

## Usage

Audit the current directory:

```bash
repolens
```

Audit somewhere else, or emit machine-readable output:

```bash
repolens ../some-project
repolens --json
repolens --markdown > repo-report.md
```

### As a CI gate

The `--min-score` flag makes repolens exit non-zero when a repo falls below a
bar you set, so you can fail a pull request that drops the project's hygiene:

```bash
repolens --min-score 85
```

A minimal GitHub Actions step:

```yaml
- run: pipx run repolens --min-score 85
```

## What it checks

| Category      | Checks                                                             |
| ------------- | ----------------------------------------------------------------- |
| Documentation | README presence & depth, changelog, contributing guide, code of conduct |
| Licensing     | A recognised license file                                         |
| CI/CD         | A CI configuration (GitHub Actions, GitLab CI, CircleCI, …)       |
| Testing       | Presence of a test suite                                          |
| Security      | Security policy, `.gitignore`, dependency automation, committed-secret scan |
| Packaging     | A build manifest and an `.editorconfig`                           |

Every check carries a weight; the score is the weighted share of checks that
pass, with warnings earning partial credit.

## Configuration

repolens works with zero configuration. To tune it, add a `.repolens.toml` to
the repo root (or a `[tool.repolens]` table in `pyproject.toml`):

```toml
min_score = 85

[secrets]
# Globs excluded from the committed-secret scan — handy for test fixtures.
ignore = ["tests/**", "docs/examples/*"]
```

## Output formats

- **default** — a coloured terminal report grouped by category
- **`--json`** — the full report as JSON, for dashboards and scripts
- **`--markdown`** — a table + suggested fixes, ideal for a CI job summary or a
  PR comment

`NO_COLOR` and `FORCE_COLOR` are both respected.

## Exit codes

| Code | Meaning                                        |
| ---- | ---------------------------------------------- |
| 0    | Audit ran; score met the threshold (if any)    |
| 1    | Score was below `--min-score`                  |
| 2    | Bad usage (e.g. the path isn't a directory)    |

## Contributing

Checks are just small functions — adding one is a few lines. See
[CONTRIBUTING.md](CONTRIBUTING.md) for the workflow and
[a walk-through of writing a check](CONTRIBUTING.md#adding-a-check).

## License

[MIT](LICENSE)
