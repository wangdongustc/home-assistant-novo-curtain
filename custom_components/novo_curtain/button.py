"""Button platform for novo_curtain."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.button import (
    ButtonEntity,
    ButtonEntityDescription,
)

from .entity import NovoCurtainEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import NovoCurtainDataUpdateCoordinator
    from .data import NovoCurtainConfigEntry


ENTITY_DESCRIPTIONS = (
    ButtonEntityDescription(key="open", name="Open Curtain"),
    ButtonEntityDescription(key="close", name="Close Curtain"),
    ButtonEntityDescription(key="jog", name="Jog Curtain"),
    ButtonEntityDescription(key="stop", name="Stop Curtain"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NovoCurtainConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    async_add_entities(
        NovoCurtainButton(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class NovoCurtainButton(NovoCurtainEntity, ButtonEntity):
    """Novo Curtain button entity."""

    def __init__(
        self,
        coordinator: NovoCurtainDataUpdateCoordinator,
        entity_description: ButtonEntityDescription,
    ) -> None:
        """Initialize the button entity."""
        super().__init__(coordinator)
        self.entity_description = entity_description

    async def async_press(self, **kwargs: Any) -> None:  # noqa: ARG002
        """Press the button."""
        client = self.coordinator.config_entry.runtime_data.client

        if self.entity_description.key == "open":
            await client.async_open_control()
        elif self.entity_description.key == "close":
            await client.async_close_control()
        elif self.entity_description.key == "jog":
            # The protocol defines dedicated open/close control commands.
            # If a distinct jog command exists, replace this call with it.
            await client.async_open_control()
        elif self.entity_description.key == "stop":
            await client.async_stop_control()
