"""External power flag (inferred: 1 while on USB power, 0 on battery). Hidden by default."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity, BinarySensorEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import SoilXConfigEntry
from .entity import SoilXEntity

DESCRIPTION = BinarySensorEntityDescription(
    key="external_power", translation_key="external_power", device_class=BinarySensorDeviceClass.PLUG,
    entity_category=EntityCategory.DIAGNOSTIC, entity_registry_enabled_default=False,
)


async def async_setup_entry(hass: HomeAssistant, entry: SoilXConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    async_add_entities([SoilXPowerSensor(entry.runtime_data)])


class SoilXPowerSensor(SoilXEntity, BinarySensorEntity):
    entity_description = DESCRIPTION

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, DESCRIPTION.key)

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.external_power
