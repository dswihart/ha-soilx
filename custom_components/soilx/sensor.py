"""Sensors: moisture, temperature, humidity, light, conductivity, pH, battery."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    LIGHT_LUX,
    PERCENTAGE,
    EntityCategory,
    UnitOfConductivity,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import SoilXConfigEntry
from .entity import SoilXEntity
from .protocol import SoilXReading


@dataclass(frozen=True, kw_only=True)
class SoilXSensorDescription(SensorEntityDescription):
    value_fn: Callable[[SoilXReading], float | int]


SENSORS: tuple[SoilXSensorDescription, ...] = (
    SoilXSensorDescription(
        key="moisture", translation_key="moisture", device_class=SensorDeviceClass.MOISTURE,
        native_unit_of_measurement=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda r: r.moisture,
    ),
    SoilXSensorDescription(
        key="temperature", device_class=SensorDeviceClass.TEMPERATURE, native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=1, value_fn=lambda r: r.temperature,
    ),
    SoilXSensorDescription(
        key="humidity", device_class=SensorDeviceClass.HUMIDITY, native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=1, value_fn=lambda r: r.humidity,
    ),
    SoilXSensorDescription(
        key="illuminance", device_class=SensorDeviceClass.ILLUMINANCE, native_unit_of_measurement=LIGHT_LUX,
        state_class=SensorStateClass.MEASUREMENT, value_fn=lambda r: r.illuminance,
    ),
    SoilXSensorDescription(
        key="conductivity", translation_key="conductivity", device_class=SensorDeviceClass.CONDUCTIVITY,
        native_unit_of_measurement=UnitOfConductivity.MICROSIEMENS_PER_CM, state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda r: r.conductivity,
    ),
    SoilXSensorDescription(
        key="ph", device_class=SensorDeviceClass.PH, state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1, value_fn=lambda r: r.ph,
    ),
    SoilXSensorDescription(
        key="battery", device_class=SensorDeviceClass.BATTERY, native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT, entity_category=EntityCategory.DIAGNOSTIC, value_fn=lambda r: r.battery,
    ),
)


async def async_setup_entry(hass: HomeAssistant, entry: SoilXConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    coordinator = entry.runtime_data
    async_add_entities(SoilXSensor(coordinator, d) for d in SENSORS)


class SoilXSensor(SoilXEntity, SensorEntity):
    entity_description: SoilXSensorDescription

    def __init__(self, coordinator, description: SoilXSensorDescription) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> float | int:
        return self.entity_description.value_fn(self.coordinator.data)
