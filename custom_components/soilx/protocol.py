"""SoilX (Mcbazel 6-in-1 Bluetooth soil meter) protocol: pure functions, no Home Assistant imports.

The meter advertises as ``Soil_Monitoring`` and exposes a vendor service ``0xFFF0``:

* ``0xFFF1`` (handle 0x0a): write a *poll* request
* ``0xFFF2`` (handle 0x0c): notifications carry the *reply*

Reverse engineered from the manufacturer's iOS app with a Bluetooth capture. Nothing here writes settings: the app only ever sends
the poll request, and so do we.

Request (10 bytes): ``68 79 00 08 01 <seq> <c1> <c2> 0d 0a``. The app counts seq 1, 2, 3; ``c1 c2`` look like a CRC16 of ``01 <seq>``.
The three requests below are the ones the app sends and are reused in a cycle.

Reply (26 bytes, big-endian)::

    0-1   68 79         header
    2-3   00 18         length (total - 2)
    4     81            reply type
    5     seq           echoes the request
    6     flag          1 on USB power, 0 on battery (inferred, see ``external_power``)
    7     battery %
    8-9   humidity x10  air relative humidity, %
    10-11 temperature x10  degrees C
    12-13 00 00         unused
    14-15 conductivity  uS/cm (reads lower than the app shows; it settles slowly)
    16    pH x10
    17    soil moisture %
    18-19 00 00         unused
    20-21 illuminance   lux
    22-23 crc16         not checked
    24-25 0d 0a         terminator
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb"
WRITE_UUID = "0000fff1-0000-1000-8000-00805f9b34fb"
NOTIFY_UUID = "0000fff2-0000-1000-8000-00805f9b34fb"
LOCAL_NAME = "Soil_Monitoring"

# The three poll requests the manufacturer's app sends (sequence numbers 1 to 3).
POLL_REQUESTS = (
    bytes.fromhex("68790008010163010d0a"),
    bytes.fromhex("68790008010253620d0a"),
    bytes.fromhex("68790008010343430d0a"),
)

REPLY_LENGTH = 26
HEADER = b"\x68\x79"
TERMINATOR = b"\x0d\x0a"
REPLY_TYPE = 0x81


class SoilXFrameError(ValueError):
    """The bytes are not a SoilX reply."""


@dataclass(frozen=True)
class SoilXReading:
    seq: int
    battery: int
    external_power: bool
    humidity: float  # %
    temperature: float  # C
    conductivity: int  # uS/cm
    ph: float
    moisture: int  # %
    illuminance: int  # lux


def parse_reply(data: bytes) -> SoilXReading:
    """Decode one reply frame. Raises SoilXFrameError for anything that is not a well-formed reply."""
    if len(data) != REPLY_LENGTH:
        raise SoilXFrameError(f"expected {REPLY_LENGTH} bytes, got {len(data)}")
    if data[0:2] != HEADER:
        raise SoilXFrameError("bad header")
    if int.from_bytes(data[2:4], "big") != REPLY_LENGTH - 2:
        raise SoilXFrameError("bad length field")
    if data[4] != REPLY_TYPE:
        raise SoilXFrameError(f"unexpected reply type 0x{data[4]:02x}")
    if data[-2:] != TERMINATOR:
        raise SoilXFrameError("bad terminator")
    return SoilXReading(
        seq=data[5],
        external_power=data[6] == 1,
        battery=data[7],
        humidity=round(int.from_bytes(data[8:10], "big") / 10, 1),
        temperature=round(int.from_bytes(data[10:12], "big") / 10, 1),
        conductivity=int.from_bytes(data[14:16], "big"),
        ph=round(data[16] / 10, 1),
        moisture=data[17],
        illuminance=int.from_bytes(data[20:22], "big"),
    )


def try_parse_reply(data: bytes) -> Optional[SoilXReading]:
    try:
        return parse_reply(data)
    except SoilXFrameError:
        return None
