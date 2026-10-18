"""Tests for burn-risk page parsing."""
import pytest

from custom_components.burn_risk.coordinator import parse_risk_page


@pytest.mark.parametrize(
    ("phrase", "expected_level", "expected_status"),
    [
        ("Low Risk", 1, "Low Risk"),
        ("Moderate Risk", 2, "Moderate Risk"),
        ("High Risk", 3, "High Risk"),
        ("Extreme Risk", 4, "Extreme Risk"),
        ("Total Ban", 5, "Total Ban"),
    ],
)
def test_parse_risk_page(phrase, expected_level, expected_status):
    """Parse each supported status."""
    assert parse_risk_page(f"<html><body><div>{phrase}</div></body></html>") == (
        expected_level,
        expected_status,
    )


def test_parse_prefers_active_status_element():
    """Prefer an active status label over a page legend."""
    html = """
    <div class="legend">Low Risk Moderate Risk High Risk Extreme Risk Total Ban</div>
    <div class="current-status active">Moderate Risk</div>
    """
    assert parse_risk_page(html) == (2, "Moderate Risk")


def test_unknown_status_raises():
    """Raise for content that has no recognized status."""
    with pytest.raises(ValueError):
        parse_risk_page("<html><body>Status unavailable</body></html>")
