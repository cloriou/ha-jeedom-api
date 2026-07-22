"""Helpers dedicated to Jeedom BLEA equipment."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.helpers.entity import EntityCategory

BLEA_PLUGIN = "blea"


def is_blea(equipment) -> bool:
    return equipment.plugin.lower() == BLEA_PLUGIN


def binary_sensor_metadata(equipment, command):
    if not is_blea(equipment):
        return {}

    logical = str(command.logical_id or "").lower()
    name = command.name.lower()

    if logical in {"present", "presentoctopi"} or "present" in name:
        return {
            "device_class": BinarySensorDeviceClass.CONNECTIVITY,
            "entity_category": EntityCategory.DIAGNOSTIC,
        }
    return {}


def device_metadata(equipment):
    if not is_blea(equipment):
        return {}

    configuration = equipment.raw.get("configuration") or {}
    model = (
        configuration.get("applyModel")
        or configuration.get("device")
        or configuration.get("name")
        or "BLEA"
    )
    manufacturer = "Xiaomi" if configuration.get("xiaomi") else "Bluetooth LE"
    return {
        "manufacturer": manufacturer,
        "model": str(model),
    }
