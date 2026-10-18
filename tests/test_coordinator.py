"""Tests for burn-risk page parsing."""
import pytest

from custom_components.burn_risk.coordinator import parse_risk_page


@pytest.mark.parametrize(
    ("value", "expected_level", "expected_status"),
    [
        (1, 1, "Low Risk"),
        (2, 2, "Moderate Risk"),
        (3, 3, "High Risk"),
        (4, 4, "Extreme Risk"),
        (5, 5, "Total Ban"),
    ],
)
def test_parse_risk_page(value, expected_level, expected_status):
    """Parse each supported numeric value."""
    html = f'<script>const risk = {{ value: {value} }};</script>'
    assert parse_risk_page(html) == (expected_level, expected_status)


def test_ignores_status_words_when_numeric_field_is_missing():
    """Do not mistake a legend for the current status."""
    html = "<html><body>Low Risk Moderate Risk High Risk Extreme Risk Total Ban</body></html>"
    with pytest.raises(ValueError):
        parse_risk_page(html)


def test_zero_is_not_a_supported_status():
    """Only values 1 through 5 map to risk labels."""
    with pytest.raises(ValueError):
        parse_risk_page("<script>const risk = { value: 0 };</script>")


def test_missing_value_raises():
    """Raise for content that has no numeric value."""
    with pytest.raises(ValueError):
        parse_risk_page("<html><body>Status unavailable</body></html>")
