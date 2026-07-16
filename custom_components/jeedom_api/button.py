"""Jeedom button platform."""
from homeassistant.components.button import ButtonEntity
from .const import CONF_SELECTED_EQUIPMENT, DOMAIN
from .discovery import button_commands
from .entity import JeedomEntity


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    selected = set(entry.options.get(CONF_SELECTED_EQUIPMENT, []))
    entities = []
    for eq_id, eq in coordinator.data.items():
        if eq_id in selected:
            entities.extend(JeedomButton(coordinator, eq, cmd) for cmd in button_commands(eq))
    async_add_entities(entities)


class JeedomButton(JeedomEntity, ButtonEntity):
    def __init__(self, coordinator, equipment, command):
        super().__init__(coordinator, equipment, unique_suffix=f"button_{command.id}")
        self.command_id = command.id
        self._attr_name = command.name

    async def async_press(self):
        await self.coordinator.api.async_execute(self.command_id)
        await self.coordinator.async_request_refresh()
