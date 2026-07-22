"""Jeedom sensor entities."""
from __future__ import annotations

import logging
from numbers import Number

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfPressure,
    UnitOfRatio,
    UnitOfTemperature,
)
from homeassistant.helpers.entity import EntityCategory

from .const import CONF_SELECTED_EQUIPMENT, DOMAIN
from .entity import JeedomEntity

_LOGGER = logging.getLogger(__name__)
INTEGRATION_SENSOR_VERSION = "0.5.3"


def _normalized(value) -> str:
    return str(value or "").strip().lower()


def _sensor_commands(equipment):
    """Return Jeedom info commands that can safely become sensors."""
    excluded = {"LIGHT_STATE", "LIGHT_BRIGHTNESS", "DONT"}
    return [
        command
        for command in equipment.info_commands()
        if command.subtype in {"numeric", "string"}
        and command.generic_type not in excluded
    ]


def _metadata(equipment, command) -> dict:
    """Map Jeedom metadata to modern Home Assistant metadata."""
    generic = _normalized(command.generic_type).upper()
    logical = _normalized(command.logical_id)
    name = _normalized(command.name)
    unit = _normalized(command.unit)
    plugin = _normalized(equipment.plugin)

    result: dict = {}

    if generic == "TEMPERATURE" or logical == "temperature" or "température" in name:
        result["device_class"] = SensorDeviceClass.TEMPERATURE
        result["unit"] = UnitOfTemperature.CELSIUS

    elif generic == "HUMIDITY" or logical in {"humidity", "moisture"} or "humidité" in name:
        result["device_class"] = SensorDeviceClass.HUMIDITY
        result["unit"] = UnitOfRatio.PERCENTAGE

    elif generic == "BATTERY" or logical == "battery" or "batterie" in name:
        result["device_class"] = SensorDeviceClass.BATTERY
        result["unit"] = UnitOfRatio.PERCENTAGE
        result["entity_category"] = EntityCategory.DIAGNOSTIC

    elif generic == "POWER":
        result["device_class"] = SensorDeviceClass.POWER
        result["unit"] = UnitOfPower.WATT

    elif generic == "ENERGY":
        result["device_class"] = SensorDeviceClass.ENERGY
        result["unit"] = UnitOfEnergy.KILO_WATT_HOUR

    elif generic == "VOLTAGE":
        result["device_class"] = SensorDeviceClass.VOLTAGE
        result["unit"] = UnitOfElectricPotential.VOLT

    elif generic == "CURRENT":
        result["device_class"] = SensorDeviceClass.CURRENT
        result["unit"] = UnitOfElectricCurrent.AMPERE

    elif generic in {"PRESSURE", "ATMOSPHERIC_PRESSURE"}:
        result["device_class"] = SensorDeviceClass.ATMOSPHERIC_PRESSURE
        result["unit"] = UnitOfPressure.HPA

    elif "rssi" in logical or "rssi" in name or unit == "dbm":
        result["device_class"] = SensorDeviceClass.SIGNAL_STRENGTH
        result["unit"] = "dBm"
        result["entity_category"] = EntityCategory.DIAGNOSTIC

    # BLEA fallback based on common command IDs/names.
    if plugin == "blea" and not result:
        if logical == "temperature":
            result["device_class"] = SensorDeviceClass.TEMPERATURE
            result["unit"] = UnitOfTemperature.CELSIUS
        elif logical in {"humidity", "moisture"}:
            result["device_class"] = SensorDeviceClass.HUMIDITY
            result["unit"] = UnitOfRatio.PERCENTAGE
        elif logical == "battery":
            result["device_class"] = SensorDeviceClass.BATTERY
            result["unit"] = UnitOfRatio.PERCENTAGE
            result["entity_category"] = EntityCategory.DIAGNOSTIC

    return result


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up selected Jeedom sensors."""
    _LOGGER.warning("Chargement de jeedom_api.sensor version %s", INTEGRATION_SENSOR_VERSION)
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    selected = set(entry.options.get(CONF_SELECTED_EQUIPMENT, []))
    entities = []

    for equipment_id, equipment in coordinator.data.items():
        if equipment_id not in selected:
            continue

        commands = _sensor_commands(equipment)
        _LOGGER.info(
            "Jeedom %s [%s] : %s capteur(s) numérique(s)/texte détecté(s)",
            equipment.name,
            equipment.plugin,
            len(commands),
        )
        entities.extend(
            JeedomSensor(coordinator, equipment, command)
            for command in commands
        )

    _LOGGER.info("Création de %s entité(s) sensor Jeedom", len(entities))
    async_add_entities(entities)


class JeedomSensor(JeedomEntity, SensorEntity):
    """One Jeedom info command exposed as a Home Assistant sensor."""

    _attr_device_class = None
    _attr_native_unit_of_measurement = None
    _attr_entity_category = None
    _attr_state_class = None

    def __init__(self, coordinator, equipment, command) -> None:
        super().__init__(
            coordinator,
            equipment,
            unique_suffix=f"sensor_{command.id}",
        )
        self.command_id = command.id
        self.command_subtype = command.subtype
        self._attr_name = command.name

        metadata = _metadata(equipment, command)
        device_class = metadata.get("device_class")
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = (
            metadata.get("unit") or command.unit or None
        )
        self._attr_entity_category = metadata.get("entity_category")

        # Only numeric sensors may have a measurement state class.
        if command.subtype == "numeric":
            if device_class == SensorDeviceClass.ENERGY:
                self._attr_state_class = SensorStateClass.TOTAL_INCREASING
            else:
                self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        equipment = self.equipment
        if equipment is None:
            return None

        command = next(
            (
                item
                for item in equipment.commands
                if item.id == self.command_id
            ),
            None,
        )
        if command is None:
            return None

        value = command.state
        if self.command_subtype != "numeric":
            return value

        if value in (None, ""):
            return None

        # Preserve numeric values as numbers instead of strings.
        if isinstance(value, Number):
            return value

        try:
            number = float(str(value).replace(",", "."))
            return int(number) if number.is_integer() else number
        except (TypeError, ValueError):
            _LOGGER.warning(
                "Valeur non numérique pour %s/%s : %r",
                equipment.name,
                command.name,
                value,
            )
            return None
