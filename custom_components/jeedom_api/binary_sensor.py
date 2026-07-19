"""Jeedom binary sensor entities."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_SELECTED_EQUIPMENT, DOMAIN
from .blea import binary_sensor_metadata
from .entity import JeedomEntity

GENERIC_DEVICE_CLASSES = {
    "PRESENCE": BinarySensorDeviceClass.PRESENCE,
    "MOTION": BinarySensorDeviceClass.MOTION,
    "OPENING": BinarySensorDeviceClass.OPENING,
    "DOOR": BinarySensorDeviceClass.DOOR,
    "WINDOW": BinarySensorDeviceClass.WINDOW,
    "SMOKE": BinarySensorDeviceClass.SMOKE,
    "MOISTURE": BinarySensorDeviceClass.MOISTURE,
    "CONNECTIVITY": BinarySensorDeviceClass.CONNECTIVITY,
}


def _binary_commands(equipment):
    excluded = {"LIGHT_STATE"}
    return [
        cmd
        for cmd in equipment.info_commands()
        if cmd.subtype == "binary"
        and cmd.generic_type not in excluded
        and cmd.generic_type != "DONT"
    ]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    selected = set(entry.options.get(CONF_SELECTED_EQUIPMENT, []))
    entities = []
    for eq_id, equipment in coordinator.data.items():
        if eq_id not in selected:
            continue
        entities.extend(
            JeedomBinarySensor(coordinator, equipment, cmd)
            for cmd in _binary_commands(equipment)
        )
    async_add_entities(entities)


class JeedomBinarySensor(JeedomEntity, BinarySensorEntity):
    """One Jeedom binary info command."""

    def __init__(self, coordinator, equipment, command) -> None:
        super().__init__(
            coordinator, equipment, unique_suffix=f"binary_sensor_{command.id}"
        )
        self.command_id = command.id
        self._attr_name = command.name

        generic = command.generic_type or ""
        for token, device_class in GENERIC_DEVICE_CLASSES.items():
            if token in generic:
                self._attr_device_class = device_class
                break

        metadata = binary_sensor_metadata(equipment, command)
        if metadata.get("device_class") is not None:
            self._attr_device_class = metadata["device_class"]
        if metadata.get("entity_category") is not None:
            self._attr_entity_category = metadata["entity_category"]

    @property
    def is_on(self) -> bool | None:
        equipment = self.equipment
        if not equipment:
            return None
        command = next(
            (cmd for cmd in equipment.commands if cmd.id == self.command_id), None
        )
        if command is None or command.state in (None, ""):
            return None
        try:
            value = bool(int(command.state))
        except (TypeError, ValueError):
            value = str(command.state).lower() in {"true", "on", "yes"}
        invert = str(command.configuration.get("invertBinary", "0")) == "1"
        return not value if invert else value
