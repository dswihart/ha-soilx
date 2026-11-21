"""Polls the meter: connect, ask for one reading, disconnect.

The meter accepts a single Bluetooth connection, so the connection is closed after every read. That leaves the gaps the
manufacturer's phone app needs if you want to use it too.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import TYPE_CHECKING

from bleak.exc import BleakError
from bleak_retry_connector import BleakClientWithServiceCache, establish_connection
from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN
from .protocol import NOTIFY_UUID, POLL_REQUESTS, WRITE_UUID, SoilXReading, try_parse_reply

if TYPE_CHECKING:
    from . import SoilXConfigEntry

_LOGGER = logging.getLogger(__name__)
REPLY_TIMEOUT = 10.0


class SoilXCoordinator(DataUpdateCoordinator[SoilXReading]):
    config_entry: "SoilXConfigEntry"

    def __init__(self, hass: HomeAssistant, entry: "SoilXConfigEntry") -> None:
        interval = int(entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
        super().__init__(hass, _LOGGER, name=DOMAIN, config_entry=entry, update_interval=timedelta(seconds=interval))
        assert entry.unique_id is not None
        self.address: str = entry.unique_id
        self._lock = asyncio.Lock()
        self._seq = 0

    async def _async_update_data(self) -> SoilXReading:
        async with self._lock:
            device = bluetooth.async_ble_device_from_address(self.hass, self.address, connectable=True)
            if device is None:
                raise UpdateFailed("The meter is not in range or is asleep (it switches off after a few minutes on battery)")
            try:
                client = await establish_connection(BleakClientWithServiceCache, device, self.address, max_attempts=3)
            except (BleakError, TimeoutError, asyncio.TimeoutError) as err:
                raise UpdateFailed(f"Could not connect to the meter: {err}") from err
            future: asyncio.Future[SoilXReading] = self.hass.loop.create_future()

            def _on_notify(_char, data: bytearray) -> None:
                reading = try_parse_reply(bytes(data))
                if reading is not None and not future.done():
                    future.set_result(reading)

            try:
                await client.start_notify(NOTIFY_UUID, _on_notify)
                request = POLL_REQUESTS[self._seq % len(POLL_REQUESTS)]
                self._seq += 1
                await client.write_gatt_char(WRITE_UUID, request, response=True)
                return await asyncio.wait_for(future, REPLY_TIMEOUT)
            except (BleakError, TimeoutError, asyncio.TimeoutError) as err:
                raise UpdateFailed(f"The meter did not answer: {err}") from err
            finally:
                try:
                    await client.disconnect()
                except BleakError:  # already gone
                    pass
