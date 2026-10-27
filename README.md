# Home Assistant: Mississippi Mills Burn Risk

A custom Home Assistant integration for the **Mississippi Mills, Ontario area only at this time**. It polls [mm.burnpermits.com](https://mm.burnpermits.com) and exposes the current burn-risk status as sensors.

The integration reads the numeric value field from the upstream page, matching the field used by the original shell script. It does not infer the current risk from words in the page legend.

## Sensors

After adding the integration, two sensors are created:

| Sensor | Value |
| --- | --- |
| **Burn Risk Level** | Numeric risk level from 1 to 5 |
| **Burn Risk Status** | Human-readable status |

The numeric values are stable for use in automations:

| Level | Status |
| ---: | --- |
| 1 | Low Risk |
| 2 | Moderate Risk |
| 3 | High Risk |
| 4 | Extreme Risk |
| 5 | Total Ban |

Both sensors include the `stale` and `source` attributes. If a refresh fails after a successful read, the integration keeps the last known value and sets `stale: true`. If it cannot retrieve an initial value, setup fails so Home Assistant can report the problem instead of showing an invented status.

## Installation

### HACS (custom repository)

1. In HACS, open **Integrations**.
2. Open the three-dot menu and select **Custom repositories**.
3. Add `https://github.com/dvinceXX/home-assistant-burn-risk` as an **Integration**.
4. Install **Mississippi Mills Burn Risk** and restart Home Assistant.
5. Go to **Settings → Devices & services → Add integration** and search for **Mississippi Mills Burn Risk**.

### Manual

Copy the `custom_components/burn_risk` directory into your Home Assistant configuration's `custom_components` directory, then restart Home Assistant and add the integration from **Settings → Devices & services**.

## Configuration

The config flow defaults to `https://mm.burnpermits.com`. You can provide a different HTTP(S) status page URL if needed. The integration polls every 15 minutes.

## Notes

This integration depends on the upstream page continuing to publish its numeric value field. If the website changes that field, the parser may need to be updated.
