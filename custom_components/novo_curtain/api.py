"""Novo Motor 485 Serial Port API Client."""

from __future__ import annotations

import asyncio
import logging
from enum import IntEnum
from typing import Any

import async_timeout
import serial  # noqa: TC002

_LOGGER = logging.getLogger(__name__)


class NovoSerialClientError(Exception):
    """Exception to indicate a general API error."""


class NovoSerialClientCommunicationError(
    NovoSerialClientError,
):
    """Exception to indicate a communication error."""


class NovoSerialClientDeviceAddressError(
    NovoSerialClientError,
):
    """Exception to indicate a mismatched device address."""


class NovoSerialCommand(IntEnum):
    """Novo Motor 485 Serial Port Command."""

    SET_POSITION = 0x67
    QUERY_STATUS = 0x98
    SET_DIRECTION = 0xCD
    OPEN_CONTROL = 0xDD
    CLOSE_CONTROL = 0xEE
    INCHING_LEFT = 0xD1
    INCHING_RIGHT = 0xE1
    STOP_CONTROL = 0xCC


class NovoSerialClient:
    """Novo Motor 485 Serial Port Client."""

    PROTOCOL_LENGTH = 9
    PROTOCOL_HEADER = 0x55
    PARAMS_LENGTH = 3

    def __init__(
        self,
        serial: serial.Serial,
        address: int,
        channel: int,
        direction: int | None = None,
    ) -> None:
        """Initialize the API client."""
        self._serial = serial
        self._lock = asyncio.Lock()
        self._addr_hi = (address >> 8) & 0xFF
        self._addr_lo = address & 0xFF
        self._channel = channel
        self._direction = direction

    def calc_checksum(self, data: list[int]) -> int:
        """Calculate the checksum for a command."""
        return sum(data) & 0xFF

    def build_command(self, command: int, params: list[int] | None = None) -> bytes:
        """Build a command to send to the curtain."""
        if params is None:
            params = []
        if len(params) != self.PARAMS_LENGTH:
            params = [*params, 0x00, 0x00, 0x00][: self.PARAMS_LENGTH]
        command_bytes = [
            self.PROTOCOL_HEADER,
            self._addr_hi,
            self._addr_lo,
            self._channel,
            command,
            *params,
        ]
        checksum = self.calc_checksum(command_bytes)
        _LOGGER.error("Checksum: %s, all: %s", checksum, command_bytes)
        return bytes([*command_bytes, checksum])

    def parse_response(self, data: bytes) -> dict[str, Any]:
        """Parse a response from the curtain."""
        if len(data) != self.PROTOCOL_LENGTH or data[0] != self.PROTOCOL_HEADER:
            error_msg = f"Invalid response length: {len(data)}"
            raise NovoSerialClientCommunicationError(error_msg)
        if data[0] != self.PROTOCOL_HEADER:
            error_msg = f"Invalid response header: {data[0]:02X}"
            raise NovoSerialClientCommunicationError(error_msg)
        if data[1] != self._addr_hi or data[2] != self._addr_lo:
            # If address mismatch, it's likely that the response is from another device
            # on the same bus, so we raise a specific error for this case to allow
            # the caller to decide how to handle it (e.g. wait for the next response)
            error_msg = f"Mismatched response address: {data[1]:02X}{data[2]:02X}"
            raise NovoSerialClientDeviceAddressError(error_msg)
        if data[3] != self._channel:
            error_msg = f"Invalid response channel: {data[3]:02X}"
            raise NovoSerialClientCommunicationError(error_msg)
        checksum = self.calc_checksum(list(data[:-1]))
        if data[-1] != checksum:
            error_msg = (
                f"Invalid response checksum: {data[-1]:02X} (expected {checksum:02X})"
            )
            raise NovoSerialClientCommunicationError(error_msg)
        return {
            "command": data[4],
            "params": list(data[5:-1]),
        }

    async def async_transaction(
        self, command: NovoSerialCommand, params: list[int] | None = None
    ) -> list[int]:
        """Send a command and wait for the response."""
        tx_bytes = self.build_command(command=command, params=params)
        _LOGGER.info("Sending command: %s", tx_bytes.hex())
        async with self._lock:
            self._serial.reset_input_buffer()
            self._serial.reset_output_buffer()
            # Send command
            await asyncio.get_event_loop().run_in_executor(
                None, self._serial.write, tx_bytes
            )
            # Wait for response
            async with async_timeout.timeout(10):
                data = await asyncio.get_event_loop().run_in_executor(
                    None, self._serial.read, self.PROTOCOL_LENGTH
                )
            _LOGGER.info("Received response: %s", data.hex())
            # Verify response
            parsed = self.parse_response(data)
            if parsed["command"] != command:
                error_msg = (
                    f"Unexpected response command: {parsed['command']:02X} "
                    f"(expected {command:02X})"
                )
                raise NovoSerialClientCommunicationError(error_msg)

            return parsed["params"]

    async def async_set_position(self, position: int) -> None:
        """Set the curtain position."""
        await self.async_transaction(
            command=NovoSerialCommand.SET_POSITION, params=[position]
        )

    async def async_set_direction(self, direction: int) -> None:
        """Set the curtain direction. 0 for default, 1 for reverse."""
        await self.async_transaction(
            command=NovoSerialCommand.SET_DIRECTION, params=[direction]
        )

    async def async_open_control(self) -> None:
        """Send open/expand control command."""
        await self.async_transaction(command=NovoSerialCommand.OPEN_CONTROL)

    async def async_close_control(self) -> None:
        """Send close/shrink control command."""
        await self.async_transaction(command=NovoSerialCommand.CLOSE_CONTROL)

    async def async_inching_left(self) -> None:
        """Send left inching command."""
        await self.async_transaction(command=NovoSerialCommand.INCHING_LEFT)

    async def async_inching_right(self) -> None:
        """Send right inching command."""
        await self.async_transaction(command=NovoSerialCommand.INCHING_RIGHT)

    async def async_stop_control(self) -> None:
        """Send motor stop command."""
        await self.async_transaction(command=NovoSerialCommand.STOP_CONTROL)

    async def async_query_status(
        self,
        *,
        ensure_direction: bool = True,
    ) -> tuple[int, int, int]:
        """
        Query the curtain position, direction and motor state.

        Returns:
            tuple: (position, direction, motor_state) where direction is 0 for default,
            1 for reverse

        """
        params = await self.async_transaction(command=NovoSerialCommand.QUERY_STATUS)
        position = params[0]
        direction = params[1] if len(params) > 1 else 0
        motor_state = params[2] if len(params) > 2 else 0  # noqa: PLR2004

        if (
            ensure_direction
            and self._direction is not None
            and direction != self._direction
        ):
            await self.async_set_direction(self._direction)
            return await self.async_query_status(ensure_direction=False)

        return position, direction, motor_state

    async def async_query_position(self) -> int:
        """Query the curtain position (legacy method)."""
        position, _, _ = await self.async_query_status()
        return position
