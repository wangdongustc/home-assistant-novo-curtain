"""Constants for novo_curtain."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "novo_curtain"
ATTRIBUTION = "Data provided by Novo N99 curtain motor"

CONF_SERIAL_PATH = "serial_path"
CONF_ADDRESS = "address"
CONF_CHANNEL = "channel"
CONF_DIRECTION = "direction"
