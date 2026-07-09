from repolens.models import Finding, Report, Status, grade_for


def _finding(status: Status, weight: int, earned: float) -> Finding:
    return Finding(
        id="x",
        title="x",
        category="c",
        status=status,
        weight=weight,
        earned=earned,
        message="",
    )


def test_empty_report_scores_zero():
    assert Report(path=".").score == 0.0


def test_score_is_weighted_ratio():
    report = Report(
        path=".",
        findings=[
            _finding(Status.PASS, 10, 10),
            _finding(Status.FAIL, 10, 0),
        ],
    )
    assert report.score == 50.0


def test_skipped_findings_are_excluded_from_score():
    report = Report(
        path=".",
        findings=[
            _finding(Status.PASS, 10, 10),
            _finding(Status.SKIP, 0, 0),
        ],
    )
    assert report.score == 100.0
    assert report.counts()["skip"] == 1


def test_warning_earns_partial_credit():
    report = Report(path=".", findings=[_finding(Status.WARN, 8, 4)])
    assert report.score == 50.0


def test_grade_boundaries():
    assert grade_for(100) == "A+"
    assert grade_for(95) == "A+"
    assert grade_for(94.9) == "A"
    assert grade_for(70) == "C"
    assert grade_for(59) == "F"


def test_report_round_trips_to_dict():
    report = Report(path="/tmp/x", findings=[_finding(Status.PASS, 10, 10)])
    data = report.to_dict()
    assert data["score"] == 100.0
    assert data["grade"] == "A+"
    assert data["findings"][0]["status"] == "pass"
