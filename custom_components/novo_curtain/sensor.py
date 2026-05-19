"""Sensor platform for novo_curtain."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription

from .entity import NovoCurtainEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import NovoCurtainDataUpdateCoordinator
    from .data import NovoCurtainConfigEntry


MOTOR_STATE_STOPPED = "stopped"
MOTOR_STATE_OPENING = "opening"
MOTOR_STATE_CLOSING = "closing"
MOTOR_STATE_UNKNOWN = "unknown"

MOTOR_STATE_MAP: dict[int, str] = {
    0: MOTOR_STATE_STOPPED,
    1: MOTOR_STATE_OPENING,
    2: MOTOR_STATE_CLOSING,
}


ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="motor_state",
        name="Motor State",
    ),
)


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: NovoCurtainConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        NovoCurtainMotorStateSensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class NovoCurtainMotorStateSensor(NovoCurtainEntity, SensorEntity):
    """Novo Curtain motor state sensor."""

    def __init__(
        self,
        coordinator: NovoCurtainDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor entity."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        )

    @property
    def native_value(self) -> str | None:
        """Return the current motor state."""
        if self.coordinator.data is None:
            return None

        motor_state = self.coordinator.data[2]
        return MOTOR_STATE_MAP.get(motor_state, MOTOR_STATE_UNKNOWN)

    @property
    def extra_state_attributes(self) -> dict[str, int] | None:
        """Return raw motor state attributes."""
        if self.coordinator.data is None:
            return None

        return {
            "position": self.coordinator.data[0],
            "direction": self.coordinator.data[1],
            "motor_state_code": self.coordinator.data[2],
        }
