import unittest

from src.pipeline.helpers.segments import catch_zone_isin_fao_zone


class TestHelpersSegments(unittest.TestCase):
    def test_catch_zone_isin_fao_zone(self):
        self.assertTrue(catch_zone_isin_fao_zone("27", "27"))
        self.assertTrue(catch_zone_isin_fao_zone("27.7", "27"))
        self.assertTrue(catch_zone_isin_fao_zone("27.7", None))
        self.assertFalse(catch_zone_isin_fao_zone(None, "27.7"))
        self.assertFalse(catch_zone_isin_fao_zone("27", "27.7"))

        self.assertTrue(catch_zone_isin_fao_zone(None, None))
