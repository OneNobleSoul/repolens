"""Command-line entry point for repolens."""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .audit import audit_repo
from .colors import Palette, should_color
from .discovery import Repo
from .report import render_json, render_markdown, render_text

# Exit codes
EXIT_OK = 0
EXIT_BELOW_THRESHOLD = 1
EXIT_USAGE = 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="repolens",
        description="Audit a repository against open-source best practices.",
        epilog="Run without arguments to audit the current directory.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="path to the repository (default: current directory)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    fmt = parser.add_mutually_exclusive_group()
    fmt.add_argument(
        "--json",
        action="store_true",
        help="emit the report as JSON",
    )
    fmt.add_argument(
        "--markdown",
        action="store_true",
        help="emit the report as Markdown (handy for CI job summaries)",
    )

    parser.add_argument(
        "--min-score",
        type=float,
        metavar="N",
        default=None,
        help="exit non-zero if the score is below N (0-100) — use as a CI gate",
    )

    color = parser.add_mutually_exclusive_group()
    color.add_argument(
        "--color",
        dest="color",
        action="store_true",
        default=None,
        help="force coloured output",
    )
    color.add_argument(
        "--no-color",
        dest="color",
        action="store_false",
        help="disable coloured output",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.min_score is not None and not 0 <= args.min_score <= 100:
        parser.error("--min-score must be between 0 and 100")

    try:
        repo = Repo(args.path)
    except (NotADirectoryError, FileNotFoundError) as exc:
        print(f"repolens: {exc}", file=sys.stderr)
        return EXIT_USAGE

    report = audit_repo(repo)

    # A --min-score flag wins; otherwise fall back to .repolens.toml.
    min_score = args.min_score
    if min_score is None:
        min_score = repo.config.min_score

    if args.json:
        print(render_json(report))
    elif args.markdown:
        print(render_markdown(report))
    else:
        palette = Palette(should_color(force=args.color))
        print(render_text(report, palette))

    if min_score is not None and report.score < min_score:
        if not (args.json or args.markdown):
            print(
                f"\nrepolens: score {report.score:.0f} is below the required "
                f"{min_score:.0f}",
                file=sys.stderr,
            )
        return EXIT_BELOW_THRESHOLD

    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
