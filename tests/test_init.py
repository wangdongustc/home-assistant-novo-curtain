# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Dong Wang
"""Tests for Novo Curtain integration."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.novo_curtain.api import NovoSerialClient, NovoSerialCommand


@pytest.mark.asyncio
async def test_novo_serial_client() -> None:
    """Test the NovoSerialClient basic functionality."""
    # Mock serial
    mock_serial = MagicMock()

    # Create client
    client = NovoSerialClient(mock_serial, address=1, channel=1)

    # Test build_command
    command = client.build_command(0x67, [100])
    assert len(command) == 9  # PROTOCOL_LENGTH
    assert command[0] == 0x55  # PROTOCOL_HEADER
    assert command[4] == 0x67  # SET_POSITION command
    assert command[5] == 100  # position parameter
    # Test build_command for SET_DIRECTION
    command = client.build_command(0xCD, [1])
    assert len(command) == 9  # PROTOCOL_LENGTH
    assert command[0] == 0x55  # PROTOCOL_HEADER
    assert command[4] == 0xCD  # SET_DIRECTION command
    assert command[5] == 1  # direction parameter
    # Test parse_response
    response = bytes(
        [0x55, 0x00, 0x01, 0x01, 0x67, 0x64, 0x00, 0x00, 0x22]
    )  # Mock response with correct checksum
    parsed = client.parse_response(response)
    assert parsed["command"] == 0x67
    assert parsed["params"] == [0x64, 0x00, 0x00]


@pytest.mark.asyncio
async def test_query_status_reconfigures_direction() -> None:
    """Ensure async_query_status reconfigures direction when the device disagrees."""
    mock_serial = MagicMock()
    client = NovoSerialClient(mock_serial, address=1, channel=1, direction=1)

    first_response = [100, 0, 0]
    second_response = [100, 1, 0]

    client.async_transaction = AsyncMock(side_effect=[first_response, second_response])
    client.async_set_direction = AsyncMock()

    position, direction, motor_state = await client.async_query_status()

    client.async_set_direction.assert_called_once_with(1)
    assert position == 100
    assert direction == 1
    assert motor_state == 0


@pytest.mark.asyncio
async def test_open_close_control_commands() -> None:
    """Test open and close control command sending."""
    mock_serial = MagicMock()
    client = NovoSerialClient(mock_serial, address=1, channel=1)

    client.async_transaction = AsyncMock()

    await client.async_open_control()
    await client.async_close_control()

    client.async_transaction.assert_any_call(command=NovoSerialCommand.OPEN_CONTROL)
    client.async_transaction.assert_any_call(command=NovoSerialCommand.CLOSE_CONTROL)


@pytest.mark.asyncio
async def test_inching_control_commands() -> None:
    """Test inching left/right control command sending."""
    mock_serial = MagicMock()
    client = NovoSerialClient(mock_serial, address=1, channel=1)

    client.async_transaction = AsyncMock()

    await client.async_inching_left()
    await client.async_inching_right()

    client.async_transaction.assert_any_call(command=NovoSerialCommand.INCHING_LEFT)
    client.async_transaction.assert_any_call(command=NovoSerialCommand.INCHING_RIGHT)


@pytest.mark.asyncio
async def test_stop_control_command() -> None:
    """Test stop control command sending."""
    mock_serial = MagicMock()
    client = NovoSerialClient(mock_serial, address=1, channel=1)

    client.async_transaction = AsyncMock()
    await client.async_stop_control()

    client.async_transaction.assert_called_once_with(
        command=NovoSerialCommand.STOP_CONTROL
    )
