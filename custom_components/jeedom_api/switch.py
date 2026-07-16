"""Jeedom switch platform."""
from homeassistant.components.switch import SwitchEntity
from .const import CONF_SELECTED_EQUIPMENT, DOMAIN
from .discovery import SWITCH_ON, SWITCH_OFF, SWITCH_STATE, command_by_types, is_switch
from .entity import JeedomEntity


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    selected = set(entry.options.get(CONF_SELECTED_EQUIPMENT, []))
    async_add_entities(
        JeedomSwitch(coordinator, eq)
        for eq_id, eq in coordinator.data.items()
        if eq_id in selected and is_switch(eq)
    )


class JeedomSwitch(JeedomEntity, SwitchEntity):
    _attr_name = None

    def __init__(self, coordinator, equipment):
        super().__init__(coordinator, equipment, unique_suffix="switch")
        self._on = command_by_types(equipment, SWITCH_ON)
        self._off = command_by_types(equipment, SWITCH_OFF)
        self._state = command_by_types(equipment, SWITCH_STATE)
        if self._state is None:
            linked_id = (self._on.value if self._on else None) or (self._off.value if self._off else None)
            self._state = next((cmd for cmd in equipment.commands if cmd.id == linked_id), None)

    @property
    def is_on(self):
        if self._state is None or self.equipment is None:
            return None
        cmd = next((cmd for cmd in self.equipment.commands if cmd.id == self._state.id), None)
        if cmd is None or cmd.state in (None, ""):
            return None
        try:
            return bool(int(cmd.state))
        except (TypeError, ValueError):
            return str(cmd.state).lower() in {"true", "on", "yes"}

    async def async_turn_on(self, **kwargs):
        if self._on:
            await self.coordinator.api.async_execute(self._on.id)
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        if self._off:
            await self.coordinator.api.async_execute(self._off.id)
            await self.coordinator.async_request_refresh()
