# Security Policy

## Supported versions

repolens is pre-1.0. Security fixes are applied to the latest released
version on PyPI and the `main` branch.

## Reporting a vulnerability

Please **do not** open a public issue for security problems.

Instead, use GitHub's [private vulnerability
reporting](https://github.com/OneNobleSoul/repolens/security/advisories/new)
(Security → Report a vulnerability). If that is unavailable to you, open a
minimal issue asking for a private contact channel without disclosing details.

When reporting, please include:

- a description of the issue and its impact,
- the version or commit affected, and
- steps to reproduce, if possible.

You can expect an acknowledgement within a few days. Once a fix is available,
we'll credit you in the release notes unless you'd prefer to stay anonymous.

## Scope

repolens reads files from a local repository and never transmits them
anywhere. The most security-relevant surface is the committed-secret scanner:
if you find a way to make it miss an obvious credential or crash on crafted
input, that's worth reporting.
