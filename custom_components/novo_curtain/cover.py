"""Switch platform for novo_curtain."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.cover import (
    CoverDeviceClass,
    CoverEntity,
    CoverEntityDescription,
    CoverEntityFeature,
)

from .entity import NovoCurtainEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import NovoCurtainDataUpdateCoordinator
    from .data import NovoCurtainConfigEntry

ENTITY_DESCRIPTIONS = (
    CoverEntityDescription(key="Novo Curtain", device_class=CoverDeviceClass.CURTAIN),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: NovoCurtainConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the cover platform."""
    async_add_entities(
        NovoCurtainCover(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class NovoCurtainCover(NovoCurtainEntity, CoverEntity):
    """novo_curtain cover class."""

    _attr_device_class = CoverDeviceClass.CURTAIN
    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.SET_POSITION
    )

    def __init__(
        self,
        coordinator: NovoCurtainDataUpdateCoordinator,
        entity_description: SwitchEntityDescription,
    ) -> None:
        """Initialize the cover class."""
        super().__init__(coordinator)
        self.entity_description = entity_description

    @property
    def current_cover_position(self) -> int | None:
        """Return the current position of the cover."""
        return self.coordinator.data

    @property
    def is_closed(self) -> bool:
        """Return true if the cover is closed."""
        return self.coordinator.data == 0

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the cover."""
        await self.coordinator.config_entry.runtime_data.client.async_set_position(100)

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close the cover."""
        await self.coordinator.config_entry.runtime_data.client.async_set_position(0)

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """Set the cover to a specific position."""
        position = kwargs["position"]
        await self.coordinator.config_entry.runtime_data.client.async_set_position(
            position
        )
