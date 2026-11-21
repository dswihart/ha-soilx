"""SoilX Soil Meter (Mcbazel 6-in-1 Bluetooth soil meter)."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import SoilXCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.BUTTON]

type SoilXConfigEntry = ConfigEntry[SoilXCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: SoilXConfigEntry) -> bool:
    coordinator = SoilXCoordinator(hass, entry)
    await coordinator.async_refresh()  # do not block set-up while the meter sleeps
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    return True


async def _async_options_updated(hass: HomeAssistant, entry: SoilXConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: SoilXConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
