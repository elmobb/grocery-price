import unittest

from datetime import datetime


class TestCleanUpdateTime(unittest.TestCase):
    def setUp(self):
        from utils.load_item_files import clean_item_update_time
        self.func = clean_item_update_time

    def test(self):
        self.assertIsNone(self.func(None))
        self.assertEqual(datetime(2018, 1, 1, 1, 1, 1), self.func(datetime(2018, 1, 1, 1, 1, 1)))
        self.assertEqual(datetime(2018, 1, 1, 1, 1, 1), self.func("2018-01-01 01:01:01"))
        self.assertEqual(datetime(2018, 10, 6, 14, 39, 19, 558000), self.func(1538836759558.0))  # UTC time.
        self.assertEqual(datetime(2018, 10, 6, 14, 39, 19, 558000), self.func(1538836759.558))  # UTC time.


class TestCleanPrice(unittest.TestCase):
    def setUp(self):
        from utils.load_item_files import clean_item_price
        self.func = clean_item_price

    def test(self):
        self.assertIsNone(self.func(None))
        self.assertEqual(float(1), self.func(int(1)))
        self.assertEqual(float(1), self.func(float(1)))
        self.assertEqual(float(1), self.func("1"))
        self.assertEqual(0.1, self.func("0.1"))
