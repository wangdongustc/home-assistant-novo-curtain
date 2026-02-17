"""
Custom integration to integrate novo_curtain with Home Assistant.

For more details about this integration, please refer to
https://github.com/wangdongustc/home-assistant-novo-curtain
"""

from __future__ import annotations

import serial

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.loader import async_get_loaded_integration

from .api import NovoSerialClient
from .const import DOMAIN, LOGGER, CONF_SERIAL_PATH, CONF_ADDRESS, CONF_CHANNEL
from .coordinator import NovoCurtainDataUpdateCoordinator
from .data import NovoCurtainData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import NovoCurtainConfigEntry

PLATFORMS: list[Platform] = [
    Platform.COVER,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: NovoCurtainConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    coordinator = NovoCurtainDataUpdateCoordinator(
        hass=hass,
        logger=LOGGER,
        name=DOMAIN,
        update_interval=timedelta(hours=1),
    )
    entry.runtime_data = NovoCurtainData(
        client=NovoSerialClient(
            serial=serial.Serial(
                entry.data[CONF_SERIAL_PATH], baudrate=9600, timeout=1
            ),
            address=int(entry.data[CONF_ADDRESS], base=0),
            channel=int(entry.data[CONF_CHANNEL], base=0),
        ),
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: NovoCurtainConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: NovoCurtainConfigEntry,
) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
