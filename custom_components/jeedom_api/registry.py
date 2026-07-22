from homeassistant.helpers import device_registry as dr, entity_registry as er
from .const import DOMAIN
from .discovery import button_commands, is_cover, is_light, is_switch

def expected_unique_ids(eq):
    ids = set()
    if is_light(eq): ids.add(f"{eq.id}_light")
    if is_switch(eq): ids.add(f"{eq.id}_switch")
    if is_cover(eq): ids.add(f"{eq.id}_cover")
    for cmd in eq.info_commands():
        if cmd.generic_type in {"LIGHT_STATE", "LIGHT_BRIGHTNESS", "DONT"}:
            continue
        if cmd.subtype == "binary":
            ids.add(f"{eq.id}_binary_sensor_{cmd.id}")
        elif cmd.subtype in {"numeric", "string"}:
            ids.add(f"{eq.id}_sensor_{cmd.id}")
    for cmd in button_commands(eq):
        ids.add(f"{eq.id}_button_{cmd.id}")
    return ids

async def async_sync_registries(hass, entry, equipment, selected):
    ent_reg = er.async_get(hass)
    dev_reg = dr.async_get(hass)
    expected = set()
    for eq_id in selected:
        if eq_id in equipment:
            expected |= expected_unique_ids(equipment[eq_id])
    for item in list(er.async_entries_for_config_entry(ent_reg, entry.entry_id)):
        if item.platform == DOMAIN and item.unique_id not in expected:
            ent_reg.async_remove(item.entity_id)
    for device in list(dr.async_entries_for_config_entry(dev_reg, entry.entry_id)):
        jeedom_ids = {ident for domain, ident in device.identifiers if domain == DOMAIN}
        if jeedom_ids and jeedom_ids.isdisjoint(selected):
            dev_reg.async_remove_device(device.id)

async def async_remove_device(hass, entry, device):
    jeedom_ids = {ident for domain, ident in device.identifiers if domain == DOMAIN}
    if not jeedom_ids:
        return False
    selected = list(entry.options.get("selected_equipment", []))
    updated = [eq_id for eq_id in selected if eq_id not in jeedom_ids]
    if updated == selected:
        return False
    options = dict(entry.options)
    options["selected_equipment"] = updated
    hass.config_entries.async_update_entry(entry, options=options)
    return True
