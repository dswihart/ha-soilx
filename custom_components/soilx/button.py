"""Sync now button: connect to the meter and read it immediately."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import SoilXConfigEntry
from .entity import SoilXEntity

DESCRIPTION = ButtonEntityDescription(key="sync_now", translation_key="sync_now", icon="mdi:sync")


async def async_setup_entry(hass: HomeAssistant, entry: SoilXConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    async_add_entities([SoilXSyncButton(entry.runtime_data)])


class SoilXSyncButton(SoilXEntity, ButtonEntity):
    entity_description = DESCRIPTION

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, DESCRIPTION.key)

    @property
    def available(self) -> bool:
        # Stay pressable while the meter is asleep, so a press can catch it awake.
        return True

    async def async_press(self) -> None:
        await self.coordinator.async_request_refresh()
