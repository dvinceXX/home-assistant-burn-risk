"""Constants for the Burn Risk integration."""
from typing import Final

DOMAIN: Final = "burn_risk"
DEFAULT_URL: Final = "https://mm.burnpermits.com"
DEFAULT_SCAN_INTERVAL_MINUTES: Final = 15

# Numeric values are intentionally stable for automations and dashboards.
RISK_LEVELS: Final = {
    1: "Low Risk",
    2: "Moderate Risk",
    3: "High Risk",
    4: "Extreme Risk",
    5: "Total Ban",
}
