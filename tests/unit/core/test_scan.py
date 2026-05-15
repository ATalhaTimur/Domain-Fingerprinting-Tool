from core.domain.entities.domain_target import DomainTarget
from core.domain.entities.risk_score import RiskScore
from core.domain.entities.scan import Scan, ScanStatus


def _make_scan() -> Scan:
    return Scan(id="test-id", target=DomainTarget("example.com"))


def test_initial_status_is_pending():
    scan = _make_scan()
    assert scan.status == ScanStatus.PENDING


def test_initial_completed_at_is_none():
    scan = _make_scan()
    assert scan.completed_at is None


def test_complete_transitions_to_completed():
    scan = _make_scan()
    scan.complete(raw_data={"key": "val"}, risk_score=RiskScore(55))
    assert scan.status == ScanStatus.COMPLETED


def test_complete_sets_completed_at():
    scan = _make_scan()
    scan.complete(raw_data={}, risk_score=RiskScore.zero())
    assert scan.completed_at is not None


def test_complete_stores_raw_data_and_risk_score():
    scan = _make_scan()
    score = RiskScore(80)
    scan.complete(raw_data={"dns": "ok"}, risk_score=score)
    assert scan.raw_data == {"dns": "ok"}
    assert scan.risk_score == score


def test_fail_transitions_to_failed():
    scan = _make_scan()
    scan.fail("timeout")
    assert scan.status == ScanStatus.FAILED


def test_fail_writes_reason_to_raw_data():
    scan = _make_scan()
    scan.fail("connection refused")
    assert scan.raw_data["failure_reason"] == "connection refused"
