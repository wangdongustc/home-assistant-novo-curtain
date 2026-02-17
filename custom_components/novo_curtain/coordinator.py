"""DataUpdateCoordinator for novo_curtain."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import NovoSerialClientCommunicationError

if TYPE_CHECKING:
    from .data import NovoCurtainConfigEntry


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class NovoCurtainDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: NovoCurtainConfigEntry

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        # pass

        try:
            return await self.config_entry.runtime_data.client.async_query_position()
        except NovoSerialClientCommunicationError as exception:
            raise UpdateFailed(exception) from exception
