"""Helpers dedicated to Jeedom BLEA equipment."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import (
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    UnitOfTemperature,
)
from homeassistant.helpers.entity import EntityCategory

BLEA_PLUGIN = "blea"


def is_blea(equipment) -> bool:
    """Return whether an equipment comes from the Jeedom BLEA plugin."""
    return equipment.plugin.lower() == BLEA_PLUGIN


def sensor_metadata(equipment, command):
    """Return HA metadata for a BLEA numeric/string info command."""
    if not is_blea(equipment):
        return {}

    generic = (command.generic_type or "").upper()
    logical = (command.logical_id or "").lower()
    name = command.name.lower()

    if generic == "TEMPERATURE" or logical == "temperature":
        return {
            "device_class": SensorDeviceClass.TEMPERATURE,
            "unit": UnitOfTemperature.CELSIUS,
        }

    if generic == "HUMIDITY" or logical in {"humidity", "moisture"}:
        return {
            "device_class": SensorDeviceClass.HUMIDITY,
            "unit": PERCENTAGE,
        }

    if generic == "BATTERY" or logical == "battery":
        return {
            "device_class": SensorDeviceClass.BATTERY,
            "unit": PERCENTAGE,
            "entity_category": EntityCategory.DIAGNOSTIC,
        }

    if (
        "rssi" in logical
        or "rssi" in name
        or str(command.unit or "").lower() in {"dbm", "dBm".lower()}
    ):
        return {
            "device_class": SensorDeviceClass.SIGNAL_STRENGTH,
            "unit": SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            "entity_category": EntityCategory.DIAGNOSTIC,
        }

    return {}


def binary_sensor_metadata(equipment, command):
    """Return HA metadata for BLEA binary info commands."""
    if not is_blea(equipment):
        return {}

    logical = (command.logical_id or "").lower()
    name = command.name.lower()

    if logical in {"present", "presentoctopi"} or "present" in name:
        return {
            "device_class": BinarySensorDeviceClass.CONNECTIVITY,
            "entity_category": EntityCategory.DIAGNOSTIC,
        }

    return {}


def device_metadata(equipment):
    """Return richer model/manufacturer metadata for a BLEA device."""
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
