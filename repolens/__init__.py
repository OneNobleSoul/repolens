"""repolens — a health check for your repository.

repolens inspects a project on disk and reports how well it follows
common open-source and engineering conventions: documentation, licensing,
CI, tests, security hygiene and packaging. It prints a human-friendly
report, can emit JSON or Markdown, and can fail your CI when a repo drops
below a score you choose.
"""

__version__ = "0.3.0"

__all__ = ["__version__"]
