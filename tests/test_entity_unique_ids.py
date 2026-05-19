"""Tests for Novo Curtain entity unique IDs."""

from custom_components.novo_curtain import button, cover, sensor
from custom_components.novo_curtain.button import NovoCurtainButton
from custom_components.novo_curtain.cover import NovoCurtainCover
from custom_components.novo_curtain.sensor import NovoCurtainMotorStateSensor


class DummyConfigEntry:
    """Simple dummy config entry for tests."""

    def __init__(self, entry_id: str) -> None:
        """Initialize a dummy config entry with an entry id."""
        self.entry_id = entry_id
        self.domain = "novo_curtain"


class DummyCoordinator:
    """Simple dummy coordinator holding a config entry for tests."""

    def __init__(self, entry_id: str) -> None:
        """Initialize the dummy coordinator with a config entry."""
        self.config_entry = DummyConfigEntry(entry_id)


def test_entities_generate_unique_ids() -> None:
    """Test that each entity gets a unique ID per config entry."""
    coordinator = DummyCoordinator(entry_id="test-entry-id")

    cover_entity = NovoCurtainCover(
        coordinator=coordinator,
        entity_description=cover.ENTITY_DESCRIPTIONS[0],
    )
    sensor_entity = NovoCurtainMotorStateSensor(
        coordinator=coordinator,
        entity_description=sensor.ENTITY_DESCRIPTIONS[0],
    )

    button_entities = [
        NovoCurtainButton(coordinator=coordinator, entity_description=desc)
        for desc in button.ENTITY_DESCRIPTIONS
    ]

    unique_ids = {
        cover_entity.unique_id,
        sensor_entity.unique_id,
        *(entity.unique_id for entity in button_entities),
    }

    assert cover_entity.unique_id == "test-entry-id_curtain"
    assert sensor_entity.unique_id == "test-entry-id_motor_state"
    assert len(unique_ids) == 1 + 1 + len(button_entities)
