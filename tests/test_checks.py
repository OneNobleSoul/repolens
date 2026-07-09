"""Behavioural tests for individual checks."""

from repolens.checks import documentation, licensing, security, testing
from repolens.models import Status


def test_readme_present_detects_file(make_repo):
    repo = make_repo({"README.md": "# hi"})
    assert documentation.readme_present(repo).status is Status.PASS


def test_readme_present_is_case_insensitive(make_repo):
    repo = make_repo({"readme.MD": "# hi"})
    assert documentation.readme_present(repo).status is Status.PASS


def test_missing_readme_fails(make_repo):
    repo = make_repo({"main.py": "print(1)"})
    finding = documentation.readme_present(repo)
    assert finding.status is Status.FAIL
    assert finding.remediation is not None


def test_thin_readme_warns(make_repo):
    repo = make_repo({"README.md": "# tiny\n"})
    assert documentation.readme_quality(repo).status is Status.WARN


def test_rich_readme_passes(make_repo):
    body = "# Project\n\n## Installation\n\n" + ("usage details. " * 60)
    repo = make_repo({"README.md": body})
    assert documentation.readme_quality(repo).status is Status.PASS


def test_license_detected(make_repo):
    repo = make_repo({"LICENSE": "MIT"})
    assert licensing.license_present(repo).status is Status.PASS


def test_tests_detected_nested(make_repo):
    repo = make_repo({"src/app.py": "x=1", "tests/test_app.py": "def test_x(): pass"})
    assert testing.tests_present(repo).status is Status.PASS


def test_tests_detected_top_level(make_repo):
    repo = make_repo({"test_app.py": "def test_x(): pass"})
    assert testing.tests_present(repo).status is Status.PASS


def test_secret_scanner_flags_aws_key(make_repo):
    repo = make_repo({"config.py": 'KEY = "AKIAIOSFODNN7EXAMPLE"'})
    finding = security.committed_secrets(repo)
    assert finding.status is Status.FAIL
    assert "AWS" in finding.message


def test_secret_scanner_flags_committed_env(make_repo):
    repo = make_repo({".env": "TOKEN=abc"})
    assert security.committed_secrets(repo).status is Status.FAIL


def test_secret_scanner_clean_repo_passes(make_repo):
    repo = make_repo({"app.py": "print('hello world')"})
    assert security.committed_secrets(repo).status is Status.PASS


def test_dependabot_detected(make_repo):
    repo = make_repo({".github/dependabot.yml": "version: 2"})
    assert security.dependency_updates(repo).status is Status.PASS
