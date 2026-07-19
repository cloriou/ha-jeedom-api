"""Base entities."""
from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .blea import device_metadata


class JeedomEntity(CoordinatorEntity):
    """Common Jeedom entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, equipment, *, unique_suffix: str) -> None:
        super().__init__(coordinator)
        self.equipment_id = equipment.id
        self._attr_unique_id = f"{equipment.id}_{unique_suffix}"
        metadata = device_metadata(equipment)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, equipment.id)},
            "name": equipment.name,
            "manufacturer": metadata.get("manufacturer", "Jeedom"),
            "model": metadata.get("model", equipment.plugin),
            "suggested_area": equipment.object_name,
        }

    @property
    def extra_state_attributes(self):
        equipment = self.equipment
        if equipment is None:
            return None
        return {
            "jeedom_equipment_id": equipment.id,
            "jeedom_plugin": equipment.plugin,
            "jeedom_object": equipment.object_name,
        }

    @property
    def equipment(self):
        return self.coordinator.data.get(self.equipment_id)

    @property
    def available(self) -> bool:
        return super().available and self.equipment is not None
