"""Jeedom light entities."""
from __future__ import annotations

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_SELECTED_EQUIPMENT, DOMAIN
from .entity import JeedomEntity

LIGHT_TYPES = {
    "LIGHT_ON",
    "LIGHT_OFF",
    "LIGHT_STATE",
    "LIGHT_BRIGHTNESS",
    "LIGHT_SLIDER",
}


def _is_light(equipment) -> bool:
    generic_types = {cmd.generic_type for cmd in equipment.commands}
    return bool(generic_types & LIGHT_TYPES) and (
        "LIGHT_ON" in generic_types or "LIGHT_OFF" in generic_types
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    selected = set(entry.options.get(CONF_SELECTED_EQUIPMENT, []))
    entities = [
        JeedomLight(coordinator, equipment)
        for eq_id, equipment in coordinator.data.items()
        if eq_id in selected and _is_light(equipment)
    ]
    async_add_entities(entities)


class JeedomLight(JeedomEntity, LightEntity):
    """A light assembled from Jeedom generic types."""

    _attr_name = None

    def __init__(self, coordinator, equipment) -> None:
        super().__init__(coordinator, equipment, unique_suffix="light")
        self._on = equipment.command_by_generic("LIGHT_ON")
        self._off = equipment.command_by_generic("LIGHT_OFF")
        self._state = equipment.command_by_generic("LIGHT_STATE")
        self._brightness = equipment.command_by_generic("LIGHT_BRIGHTNESS")
        self._slider = equipment.command_by_generic("LIGHT_SLIDER")

        if self._slider and self._brightness:
            self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}
            self._attr_color_mode = ColorMode.BRIGHTNESS
        else:
            self._attr_supported_color_modes = {ColorMode.ONOFF}
            self._attr_color_mode = ColorMode.ONOFF

    def _current_command(self, command_id):
        equipment = self.equipment
        if not equipment:
            return None
        return next((cmd for cmd in equipment.commands if cmd.id == command_id), None)

    @property
    def is_on(self) -> bool | None:
        if not self._state:
            return None
        cmd = self._current_command(self._state.id)
        return None if cmd is None else bool(int(cmd.state or 0))

    @property
    def brightness(self) -> int | None:
        if not self._brightness:
            return None
        cmd = self._current_command(self._brightness.id)
        if cmd is None or cmd.state is None:
            return None
        maximum = float(cmd.configuration.get("maxValue") or 255)
        minimum = float(cmd.configuration.get("minValue") or 0)
        value = float(cmd.state)
        if maximum <= minimum:
            return None
        return round((value - minimum) * 255 / (maximum - minimum))

    async def async_turn_on(self, **kwargs) -> None:
        if self._on:
            await self.coordinator.api.async_execute(self._on.id)

        if ATTR_BRIGHTNESS in kwargs and self._slider:
            requested = int(kwargs[ATTR_BRIGHTNESS])
            maximum = float(self._slider.configuration.get("maxValue") or 255)
            minimum = float(self._slider.configuration.get("minValue") or 0)
            jeedom_value = round(minimum + requested * (maximum - minimum) / 255)
            await self.coordinator.api.async_execute(
                self._slider.id, slider=jeedom_value
            )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        if self._off:
            await self.coordinator.api.async_execute(self._off.id)
        await self.coordinator.async_request_refresh()
