"""Switch platform for novo_curtain."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription

from .entity import NovoCurtainEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import NovoCurtainDataUpdateCoordinator
    from .data import NovoCurtainConfigEntry


ENTITY_DESCRIPTIONS = (
    SwitchEntityDescription(key="open_close_control", name="Open/Close Control"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NovoCurtainConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    async_add_entities(
        NovoCurtainOpenCloseSwitch(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class NovoCurtainOpenCloseSwitch(NovoCurtainEntity, SwitchEntity):
    """Novo Curtain open/close control switch."""

    _attr_entity_description = ENTITY_DESCRIPTIONS[0]

    def __init__(
        self,
        coordinator: NovoCurtainDataUpdateCoordinator,
        entity_description: SwitchEntityDescription,
    ) -> None:
        """Initialize the switch class."""
        super().__init__(coordinator)
        self.entity_description = entity_description

    @property
    def is_on(self) -> bool | None:
        """Return true if the curtain is open enough to consider the switch on."""
        if self.coordinator.data:
            return self.coordinator.data[0] > 0
        return None

    @property
    def extra_state_attributes(self) -> dict[str, int] | None:
        """Return motor state attributes if available."""
        if self.coordinator.data:
            return {
                "position": self.coordinator.data[0],
                "direction": self.coordinator.data[1],
                "motor_state": self.coordinator.data[2],
            }
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:  # noqa: ARG002
        """Send open control command."""
        await self.coordinator.config_entry.runtime_data.client.async_open_control()

    async def async_turn_off(self, **kwargs: Any) -> None:  # noqa: ARG002
        """Send close control command."""
        await self.coordinator.config_entry.runtime_data.client.async_close_control()
