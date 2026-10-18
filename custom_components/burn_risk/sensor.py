"""Sensor platform for Burn Risk."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import BurnRiskCoordinator
from .const import DOMAIN


@dataclass(frozen=True, kw_only=True)
class BurnRiskSensorDescription(SensorEntityDescription):
    """Describe a Burn Risk sensor."""


SENSORS = (
    BurnRiskSensorDescription(
        key="level",
        name="Level",
        icon="mdi:fire-alert",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BurnRiskSensorDescription(
        key="status",
        name="Status",
        icon="mdi:fire",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        BurnRiskSensor(coordinator, entry, description) for description in SENSORS
    )


class BurnRiskSensor(CoordinatorEntity[BurnRiskCoordinator], SensorEntity):
    """Represent one burn-risk sensor."""

    entity_description: BurnRiskSensorDescription

    def __init__(
        self,
        coordinator: BurnRiskCoordinator,
        entry: ConfigEntry,
        description: BurnRiskSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_has_entity_name = True

    @property
    def native_value(self) -> int | str | None:
        """Return the current sensor value."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data[self.entity_description.key]

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Expose data freshness and source URL."""
        if self.coordinator.data is None:
            return {}
        return {
            "stale": self.coordinator.data.get("stale", False),
            "source": self.coordinator.data.get("source"),
        }
