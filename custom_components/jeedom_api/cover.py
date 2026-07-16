"""Jeedom cover platform."""
from homeassistant.components.cover import ATTR_POSITION, CoverDeviceClass, CoverEntity, CoverEntityFeature
from .const import CONF_SELECTED_EQUIPMENT, DOMAIN
from .discovery import COVER_OPEN, COVER_CLOSE, COVER_STOP, COVER_POSITION, COVER_SET_POSITION, command_by_types, is_cover
from .entity import JeedomEntity


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    selected = set(entry.options.get(CONF_SELECTED_EQUIPMENT, []))
    async_add_entities(
        JeedomCover(coordinator, eq)
        for eq_id, eq in coordinator.data.items()
        if eq_id in selected and is_cover(eq)
    )


class JeedomCover(JeedomEntity, CoverEntity):
    _attr_name = None
    _attr_device_class = CoverDeviceClass.SHUTTER

    def __init__(self, coordinator, equipment):
        super().__init__(coordinator, equipment, unique_suffix="cover")
        self._open = command_by_types(equipment, COVER_OPEN)
        self._close = command_by_types(equipment, COVER_CLOSE)
        self._stop = command_by_types(equipment, COVER_STOP)
        self._position = command_by_types(equipment, COVER_POSITION)
        self._set_position = command_by_types(equipment, COVER_SET_POSITION)
        features = CoverEntityFeature(0)
        if self._open: features |= CoverEntityFeature.OPEN
        if self._close: features |= CoverEntityFeature.CLOSE
        if self._stop: features |= CoverEntityFeature.STOP
        if self._set_position: features |= CoverEntityFeature.SET_POSITION
        self._attr_supported_features = features

    @property
    def current_cover_position(self):
        if self._position is None or self.equipment is None:
            return None
        cmd = next((cmd for cmd in self.equipment.commands if cmd.id == self._position.id), None)
        if cmd is None or cmd.state in (None, ""):
            return None
        try:
            raw = float(cmd.state)
            minimum = float(cmd.configuration.get("minValue") or 0)
            maximum = float(cmd.configuration.get("maxValue") or 100)
            if maximum <= minimum:
                minimum, maximum = 0, 100
            return max(0, min(100, round((raw - minimum) * 100 / (maximum - minimum))))
        except (TypeError, ValueError):
            return None

    @property
    def is_closed(self):
        position = self.current_cover_position
        return None if position is None else position == 0

    async def async_open_cover(self, **kwargs):
        if self._open:
            await self.coordinator.api.async_execute(self._open.id)
            await self.coordinator.async_request_refresh()

    async def async_close_cover(self, **kwargs):
        if self._close:
            await self.coordinator.api.async_execute(self._close.id)
            await self.coordinator.async_request_refresh()

    async def async_stop_cover(self, **kwargs):
        if self._stop:
            await self.coordinator.api.async_execute(self._stop.id)
            await self.coordinator.async_request_refresh()

    async def async_set_cover_position(self, **kwargs):
        if not self._set_position:
            return
        position = int(kwargs[ATTR_POSITION])
        minimum = float(self._set_position.configuration.get("minValue") or 0)
        maximum = float(self._set_position.configuration.get("maxValue") or 100)
        raw = round(minimum + position * (maximum - minimum) / 100)
        await self.coordinator.api.async_execute(self._set_position.id, slider=raw)
        await self.coordinator.async_request_refresh()
