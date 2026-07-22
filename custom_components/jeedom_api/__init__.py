"""Jeedom API prototype integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import JeedomApi
from .const import (
    CONF_API_KEY,
    CONF_AUTO_DISCOVER,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_AUTO_DISCOVER,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import JeedomDataUpdateCoordinator
from .registry import async_remove_device, async_sync_registries
from .topology import topology_signature

_LOGGER = logging.getLogger(__name__)
INTEGRATION_VERSION = "0.5.3"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _LOGGER.warning("Chargement de Jeedom API version %s", INTEGRATION_VERSION)
    api = JeedomApi(hass, entry.data["url"], entry.data[CONF_API_KEY])
    scan_interval = int(entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
    coordinator = JeedomDataUpdateCoordinator(hass, api, scan_interval, entry)
    await coordinator.async_config_entry_first_refresh()
    selected = set(entry.options.get("selected_equipment", []))
    await async_sync_registries(hass, entry, coordinator.data, selected)
    coordinator.topology_signature = topology_signature(coordinator.data, selected)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
    }

    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))

    async def _check_topology():
        if not entry.options.get(CONF_AUTO_DISCOVER, DEFAULT_AUTO_DISCOVER):
            return
        selected_ids = set(entry.options.get("selected_equipment", []))
        signature = topology_signature(coordinator.data, selected_ids)
        if signature != coordinator.topology_signature and not coordinator.reload_scheduled:
            coordinator.reload_scheduled = True
            hass.async_create_task(hass.config_entries.async_reload(entry.entry_id))
        coordinator.topology_signature = signature

    entry.async_on_unload(coordinator.async_add_listener(_check_topology))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def _async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    _LOGGER.info("Rechargement de Jeedom API après modification des options")
    await hass.config_entries.async_reload(entry.entry_id)


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate old entries and force a clean entity rebuild."""
    _LOGGER.info(
        "Migration de l'entrée Jeedom API de la version %s vers la version 1",
        entry.version,
    )
    if entry.version < 1:
        hass.config_entries.async_update_entry(entry, version=1)
    return True

async def async_remove_config_entry_device(hass, entry, device_entry) -> bool:
    return await async_remove_device(hass, entry, device_entry)
