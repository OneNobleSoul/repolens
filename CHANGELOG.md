# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2026-07-09

### Added
- `.repolens.toml` / `[tool.repolens]` configuration, including `min_score` and
  a `secrets.ignore` glob list for the secret scanner.
- `--markdown` output for CI job summaries and PR comments.

### Changed
- The secret scanner now skips configured paths and its own source, eliminating
  false positives on test fixtures.

## [0.2.0] - 2026-07-08

### Added
- Committed-secret scanner (AWS keys, private-key blocks, provider tokens,
  stray `.env` files).
- Dependency-automation check (Dependabot / Renovate).
- `--json` output and documented exit codes.

## [0.1.0] - 2026-07-07

### Added
- Initial release: documentation, licensing, CI, testing and packaging checks
  with a weighted 0–100 score and a coloured terminal report.
- `--min-score` gate for use in CI.

[Unreleased]: https://github.com/OneNobleSoul/repolens/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/OneNobleSoul/repolens/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/OneNobleSoul/repolens/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/OneNobleSoul/repolens/releases/tag/v0.1.0
