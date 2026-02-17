"""Custom types for novo_curtain."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import NovoSerialClient
    from .coordinator import NovoCurtainDataUpdateCoordinator


type NovoCurtainConfigEntry = ConfigEntry[NovoCurtainData]


@dataclass
class NovoCurtainData:
    """Data for the NovoCurtain integration."""

    client: NovoSerialClient
    coordinator: NovoCurtainDataUpdateCoordinator
    integration: Integration
