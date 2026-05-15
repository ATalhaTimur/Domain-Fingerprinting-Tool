import pytest
from core.domain.entities.risk_score import RiskScore


def test_zero_returns_value_zero():
    assert RiskScore.zero().value == 0


def test_level_low_at_39():
    assert RiskScore(39).level == "low"


def test_level_medium_at_40():
    assert RiskScore(40).level == "medium"


def test_level_medium_at_69():
    assert RiskScore(69).level == "medium"


def test_level_critical_at_70():
    assert RiskScore(70).level == "critical"


def test_invalid_below_zero():
    with pytest.raises(ValueError):
        RiskScore(-1)


def test_invalid_above_hundred():
    with pytest.raises(ValueError):
        RiskScore(101)


def test_frozen():
    score = RiskScore(50)
    with pytest.raises(Exception):  # FrozenInstanceError is a subclass of AttributeError
        score.value = 99
