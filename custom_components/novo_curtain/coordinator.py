# SPDX-License-Identifier: Apache-2.0
"""DataUpdateCoordinator for novo_curtain."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import NovoSerialClientCommunicationError

if TYPE_CHECKING:
    from .data import NovoCurtainConfigEntry


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class NovoCurtainDataUpdateCoordinator(DataUpdateCoordinator[tuple[int, int, int]]):
    """Class to manage fetching data from the API."""

    config_entry: NovoCurtainConfigEntry

    async def _async_update_data(self) -> tuple[int, int, int]:
        """
        Update data via library.

        Returns:
            tuple: (position, direction, motor_state) where direction is 0 for default,
            1 for reverse

        """
        try:
            return await self.config_entry.runtime_data.client.async_query_status()
        except NovoSerialClientCommunicationError as exception:
            raise UpdateFailed(exception) from exception
