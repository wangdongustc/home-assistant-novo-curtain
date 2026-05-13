"""Tests for Novo Curtain integration."""

from unittest.mock import MagicMock

import pytest

from custom_components.novo_curtain.api import NovoSerialClient


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
    assert command[5] == 1     # direction parameter
    # Test parse_response
    response = bytes(
        [0x55, 0x00, 0x01, 0x01, 0x67, 0x64, 0x00, 0x00, 0x22]
    )  # Mock response with correct checksum
    parsed = client.parse_response(response)
    assert parsed["command"] == 0x67
    assert parsed["params"] == [0x64, 0x00, 0x00]
