"""Coordinator for Jeedom fullData polling."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import JeedomApi, JeedomApiError
from .models import parse_full_data

_LOGGER = logging.getLogger(__name__)


class JeedomDataUpdateCoordinator(DataUpdateCoordinator):
    """Fetch all data once and share it between entities."""

    def __init__(self, hass, api: JeedomApi, scan_interval: int, entry=None) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="Jeedom API",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.api = api
        self.entry = entry
        self.topology_signature = None
        self.reload_scheduled = False

    async def _async_update_data(self):
        try:
            payload = await self.api.async_get_full_data()
            return parse_full_data(payload)
        except JeedomApiError as err:
            raise UpdateFailed(f"Erreur Jeedom: {err}") from err
