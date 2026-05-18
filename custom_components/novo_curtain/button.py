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
    ButtonEntityDescription(key="inching_left", name="Inching Left"),
    ButtonEntityDescription(key="inching_right", name="Inching Right"),
    ButtonEntityDescription(key="stop", name="Stop Curtain"),
)


async def async_setup_entry(
    _hass: HomeAssistant,
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
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        )

    async def async_press(self, **kwargs: Any) -> None:  # noqa: ARG002
        """Press the button."""
        client = self.coordinator.config_entry.runtime_data.client

        if self.entity_description.key == "open":
            await client.async_open_control()
        elif self.entity_description.key == "close":
            await client.async_close_control()
        elif self.entity_description.key == "inching_left":
            await client.async_inching_left()
        elif self.entity_description.key == "inching_right":
            await client.async_inching_right()
        elif self.entity_description.key == "stop":
            await client.async_stop_control()
