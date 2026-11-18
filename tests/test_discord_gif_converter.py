import unittest

from discord_gif_converter import DiscordGIFConverter
from gui_converter import DiscordGIFConverterGUI


class ClipRangeTests(unittest.TestCase):
    def setUp(self):
        self.converter = object.__new__(DiscordGIFConverter)

    def test_default_clip_starts_at_requested_time(self):
        self.assertEqual(self.converter._resolve_clip(15, None, 30), (15.0, 10.0))

    def test_clip_length_is_limited_from_start(self):
        self.assertEqual(self.converter._resolve_clip(5, 25, 30), (5.0, 10.0))

    def test_unknown_video_duration_still_uses_maximum_length(self):
        self.assertEqual(self.converter._resolve_clip(12, None, 0), (12.0, 10.0))

    def test_rejects_empty_or_out_of_bounds_clip(self):
        with self.assertRaises(ValueError):
            self.converter._resolve_clip(5, 5, 30)
        with self.assertRaises(ValueError):
            self.converter._resolve_clip(30, None, 30)


class GuiTimeParsingTests(unittest.TestCase):
    def setUp(self):
        self.gui = object.__new__(DiscordGIFConverterGUI)

    def test_parses_seconds_and_clock_time(self):
        self.assertEqual(self.gui.parse_time("12.5"), 12.5)
        self.assertEqual(self.gui.parse_time("1:05"), 65)
        self.assertEqual(self.gui.parse_time("01:02:03"), 3723)
        self.assertIsNone(self.gui.parse_time(""))

    def test_rejects_invalid_time(self):
        with self.assertRaises(ValueError):
            self.gui.parse_time("1:60")
        with self.assertRaises(ValueError):
            self.gui.parse_time("-1")


if __name__ == "__main__":
    unittest.main()
