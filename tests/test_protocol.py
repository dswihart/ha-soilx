import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "custom_components", "soilx"))
import protocol as P  # noqa: E402

# Real frames captured from a meter (probes in wet soil/water, on battery) on 2026-11-21. The app showed
# moisture 96 %, pH 6.0-6.7, temperature 21.2-21.8 C, humidity 46.8 %, light 264-266 lux at the time.
BATTERY_FRAMES = [
    "687900188101005b01d000d9000003693a600000010378af0d0a",
    "687900188102005b01cf00da000003a03a6000000103bb4c0d0a",
    "687900188103005b01cf00d9000003533c600000010099cc0d0a",
    "687900188101005b01d300d9000002f03c6000000101ea340d0a",
]
# Plugged in, probes in air then cold water (older capture).
USB_FRAMES = [
    "687900188101016101ce00e00000000046000000007774ae0d0a",
    "687900188102016101cd00e0000000004600000000787bc20d0a",
]


class ParseTests(unittest.TestCase):
    def test_battery_frame(self):
        r = P.parse_reply(bytes.fromhex(BATTERY_FRAMES[0]))
        self.assertEqual(r.seq, 1)
        self.assertEqual(r.battery, 91)
        self.assertFalse(r.external_power)
        self.assertEqual(r.humidity, 46.4)
        self.assertEqual(r.temperature, 21.7)
        self.assertEqual(r.conductivity, 873)
        self.assertEqual(r.ph, 5.8)
        self.assertEqual(r.moisture, 96)
        self.assertEqual(r.illuminance, 259)

    def test_usb_frame(self):
        r = P.parse_reply(bytes.fromhex(USB_FRAMES[0]))
        self.assertTrue(r.external_power)
        self.assertEqual(r.battery, 97)
        self.assertEqual(r.humidity, 46.2)
        self.assertEqual(r.temperature, 22.4)
        self.assertEqual(r.ph, 7.0)
        self.assertEqual(r.moisture, 0)

    def test_all_captured_frames_parse_in_range(self):
        for h in BATTERY_FRAMES + USB_FRAMES:
            r = P.parse_reply(bytes.fromhex(h))
            self.assertTrue(0 <= r.moisture <= 100)
            self.assertTrue(0 <= r.battery <= 100)
            self.assertTrue(0 <= r.humidity <= 100)
            self.assertTrue(0 <= r.ph <= 14)
            self.assertTrue(-20 <= r.temperature <= 80)

    def test_rejects_malformed(self):
        good = bytes.fromhex(BATTERY_FRAMES[0])
        for bad in (
            good[:-1],  # short
            good + b"\x00",  # long
            b"\x00\x79" + good[2:],  # header
            good[:3] + b"\x19" + good[4:],  # length field
            good[:4] + b"\x80" + good[5:],  # type
            good[:-1] + b"\x00",  # terminator
            b"",
        ):
            with self.assertRaises(P.SoilXFrameError):
                P.parse_reply(bad)
            self.assertIsNone(P.try_parse_reply(bad))

    def test_poll_requests_are_the_apps(self):
        self.assertEqual(len(P.POLL_REQUESTS), 3)
        for i, req in enumerate(P.POLL_REQUESTS, start=1):
            self.assertEqual(len(req), 10)
            self.assertEqual(req[:2], P.HEADER)
            self.assertEqual(int.from_bytes(req[2:4], "big"), 8)
            self.assertEqual(req[5], i)
            self.assertEqual(req[-2:], P.TERMINATOR)


if __name__ == "__main__":
    unittest.main()
