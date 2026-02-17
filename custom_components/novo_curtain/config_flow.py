"""Adds config flow for Blueprint."""

from __future__ import annotations

import serial

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from slugify import slugify

from .api import (
    NovoSerialClient,
    NovoSerialClientError,
)
from .const import DOMAIN, LOGGER, CONF_SERIAL_PATH, CONF_ADDRESS, CONF_CHANNEL


class NovoCurtainFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for NovoCurtain."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self._test_credentials(
                    serial_path=user_input[CONF_SERIAL_PATH],
                    address=user_input[CONF_ADDRESS],
                    channel=user_input[CONF_CHANNEL],
                )
            except NovoSerialClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(
                    ## Do NOT use this in production code
                    ## The unique_id should never be something that can change
                    ## https://developers.home-assistant.io/docs/config_entries_config_flow_handler#unique-ids
                    unique_id=slugify(user_input[CONF_SERIAL_PATH])
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_SERIAL_PATH],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SERIAL_PATH,
                        default=(user_input or {}).get(CONF_SERIAL_PATH, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Required(CONF_ADDRESS): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.NUMBER,
                        ),
                    ),
                    vol.Required(CONF_CHANNEL): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0x01,
                            max=0xFE,
                            step=1,
                        ),
                    ),
                },
            ),
            errors=_errors,
        )

    async def _test_credentials(
        self, serial_path: str, address: str, channel: int
    ) -> None:
        """Validate credentials."""
        serial_port = serial.Serial(serial_path, baudrate=9600, timeout=1)
        address_int = int(address, base=0)
        client = NovoSerialClient(
            serial=serial_port, address=address_int, channel=channel
        )
        await client.async_query_position()
