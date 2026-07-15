"""Jeedom sensor entities."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfPressure,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_SELECTED_EQUIPMENT, DOMAIN
from .entity import JeedomEntity

GENERIC_MAP = {
    "TEMPERATURE": (SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS),
    "HUMIDITY": (SensorDeviceClass.HUMIDITY, PERCENTAGE),
    "POWER": (SensorDeviceClass.POWER, UnitOfPower.WATT),
    "ENERGY": (SensorDeviceClass.ENERGY, UnitOfEnergy.KILO_WATT_HOUR),
    "VOLTAGE": (SensorDeviceClass.VOLTAGE, UnitOfElectricPotential.VOLT),
    "CURRENT": (SensorDeviceClass.CURRENT, UnitOfElectricCurrent.AMPERE),
    "PRESSURE": (SensorDeviceClass.ATMOSPHERIC_PRESSURE, UnitOfPressure.HPA),
    "BATTERY": (SensorDeviceClass.BATTERY, PERCENTAGE),
}


def _sensor_commands(equipment):
    # Light state and brightness are attributes of light, not duplicate sensors.
    excluded = {"LIGHT_STATE", "LIGHT_BRIGHTNESS"}
    return [
        cmd
        for cmd in equipment.info_commands()
        if cmd.subtype in {"numeric", "string"}
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
            JeedomSensor(coordinator, equipment, cmd)
            for cmd in _sensor_commands(equipment)
        )
    async_add_entities(entities)


class JeedomSensor(JeedomEntity, SensorEntity):
    """One Jeedom info command exposed as a sensor."""

    def __init__(self, coordinator, equipment, command) -> None:
        super().__init__(coordinator, equipment, unique_suffix=f"sensor_{command.id}")
        self.command_id = command.id
        self._attr_name = command.name
        self._attr_native_unit_of_measurement = command.unit

        generic = command.generic_type or ""
        for token, (device_class, default_unit) in GENERIC_MAP.items():
            if token in generic:
                self._attr_device_class = device_class
                if not self._attr_native_unit_of_measurement:
                    self._attr_native_unit_of_measurement = default_unit
                break

        if command.subtype == "numeric":
            if self._attr_device_class in {
                SensorDeviceClass.ENERGY,
            }:
                self._attr_state_class = SensorStateClass.TOTAL_INCREASING
            else:
                self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        equipment = self.equipment
        if not equipment:
            return None
        command = next(
            (cmd for cmd in equipment.commands if cmd.id == self.command_id), None
        )
        return command.state if command else None
