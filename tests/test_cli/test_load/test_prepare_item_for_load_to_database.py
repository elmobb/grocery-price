import unittest

from datetime import datetime


class TestUpdateTime(unittest.TestCase):
    def setUp(self):
        from grocery_price.cli.load import prepare_update_time
        self.func = prepare_update_time

    def test(self):
        self.assertIsNone(self.func(None))
        self.assertEqual(datetime(2018, 1, 1, 1, 1, 1), self.func(datetime(2018, 1, 1, 1, 1, 1)))
        self.assertEqual(datetime(2018, 1, 1, 1, 1, 1), self.func("2018-01-01 01:01:01"))
        self.assertEqual(datetime(2018, 10, 6, 14, 39, 19, 558000), self.func(1538836759558.0))  # UTC time.
        self.assertEqual(datetime(2018, 10, 6, 14, 39, 19, 558000), self.func(1538836759.558))  # UTC time.


class TestPrice(unittest.TestCase):
    def setUp(self):
        from grocery_price.cli.load import prepare_price
        self.func = prepare_price

    def test(self):
        self.assertIsNone(self.func(None))
        self.assertEqual(float(1), self.func(int(1)))
        self.assertEqual(float(1), self.func(float(1)))
        self.assertEqual(float(1), self.func("1"))
        self.assertEqual(0.1, self.func("0.1"))


class TestBrandName(unittest.TestCase):
    def setUp(self):
        from grocery_price.cli.load import prepare_brand_name
        self.func = prepare_brand_name

    def test(self):
        self.assertIsNone(self.func(None))
        self.assertEqual("a", self.func("a"))
