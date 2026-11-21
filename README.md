# SoilX Soil Meter for Home Assistant

A custom integration for the **Mcbazel SoilX 6-in-1 Bluetooth soil meter** (it advertises as `Soil_Monitoring`; sold on Amazon as
"Mcbazel SoilX 6-in-1 Bluetooth pH Soil Meter", item model `gf-020981`). It reads the meter locally over Bluetooth. No cloud, no
account, no phone app.

> Unofficial. Not affiliated with Mcbazel. The protocol was worked out from the meter's own app traffic, and the integration only
> ever sends the same "read" request the app sends. It never writes settings.

## Sensors

| Sensor | Unit | Notes |
|---|---|---|
| Soil moisture | % | |
| Temperature | °C | |
| Humidity | % | air humidity |
| Illuminance | lx | |
| Soil conductivity | µS/cm | right order of magnitude, but reads lower than the phone app (see Limits) |
| pH | | reads 7.0 with nothing to measure |
| Battery | % | diagnostic |
| External power | on/off | diagnostic, disabled by default, inferred from a flag in the data |

## Install

**HACS (custom repository):** HACS, three dots, Custom repositories, add `https://github.com/dswihart/ha-soilx` as an
*Integration*, download, restart Home Assistant.

**Manual:** copy `custom_components/soilx` into your Home Assistant `config/custom_components`, restart.

Then wake the meter and close the phone app. The meter is discovered automatically; confirm it under **Settings, Devices &
services**. If it is not found, choose **Add integration, SoilX Soil Meter**.

You need a Bluetooth adapter or an ESPHome Bluetooth proxy within range of the meter. It must be a *connectable* one, because the
data is read over a connection, not from broadcasts.

## How it works, and the limits

* The meter allows **one Bluetooth connection at a time**. Home Assistant connects, asks for one reading and disconnects, once a
  minute by default (30 s to 1 h, change it in the integration's options). While the phone app is connected, Home Assistant cannot
  read the meter, and the other way round.
* **On battery the meter switches itself off** after a few minutes. Keep it **plugged in with USB-C** for continuous monitoring.
* Conductivity reads lower than the phone app shows. The raw value is reported unchanged.
* Tested with one meter. Tested with Home Assistant 2026.11 on a Raspberry Pi 5.

## Protocol (for the curious)

Vendor service `0xFFF0`. Write a 10-byte request to `0xFFF1`, read the 26-byte reply from a notification on `0xFFF2`. The layout is
documented in `custom_components/soilx/protocol.py`, with tests built from real captured replies.

## Development

```
python -m unittest discover -s tests
```

The protocol module has no Home Assistant dependency, so the tests run anywhere.

## Licence

MIT
