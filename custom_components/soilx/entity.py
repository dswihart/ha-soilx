"""Shared base entity."""
from __future__ import annotations

from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SoilXCoordinator


class SoilXEntity(CoordinatorEntity[SoilXCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: SoilXCoordinator, key: str) -> None:
        super().__init__(coordinator)
        address = coordinator.address
        self._attr_unique_id = f"{address}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, address)},
            connections={(CONNECTION_BLUETOOTH, address)},
            manufacturer="Mcbazel",
            model="SoilX 6-in-1 Bluetooth soil meter",
            name=f"SoilX {address[-5:].replace(':', '')}",
        )
