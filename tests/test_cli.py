"""End-to-end tests driving the CLI the way a user (or CI) would."""

import json

import pytest

from repolens.cli import EXIT_BELOW_THRESHOLD, EXIT_OK, EXIT_USAGE, main


@pytest.fixture
def good_repo(tmp_path):
    (tmp_path / "README.md").write_text(
        "# Thing\n\n## Installation\n\n" + "usage " * 200, encoding="utf-8"
    )
    (tmp_path / "LICENSE").write_text("MIT", encoding="utf-8")
    (tmp_path / ".gitignore").write_text("*.pyc", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_x.py").write_text("def test_x(): pass", encoding="utf-8")
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text("name: ci", encoding="utf-8")
    return tmp_path


def test_json_output_is_valid(good_repo, capsys):
    code = main([str(good_repo), "--json"])
    assert code == EXIT_OK
    payload = json.loads(capsys.readouterr().out)
    assert 0 <= payload["score"] <= 100
    assert payload["grade"]


def test_min_score_gate_fails_on_empty_repo(tmp_path, capsys):
    code = main([str(tmp_path), "--min-score", "80"])
    assert code == EXIT_BELOW_THRESHOLD


def test_min_score_gate_passes_on_good_repo(good_repo):
    assert main([str(good_repo), "--min-score", "40"]) == EXIT_OK


def test_invalid_min_score_is_usage_error(tmp_path):
    with pytest.raises(SystemExit) as excinfo:
        main([str(tmp_path), "--min-score", "150"])
    assert excinfo.value.code == EXIT_USAGE


def test_missing_path_reports_usage_error(capsys):
    code = main(["/does/not/exist/repolens", "--json"])
    assert code == EXIT_USAGE
    assert "repolens:" in capsys.readouterr().err


def test_markdown_output_has_table(good_repo, capsys):
    main([str(good_repo), "--markdown"])
    out = capsys.readouterr().out
    assert "| Category |" in out
    assert "repolens report" in out
