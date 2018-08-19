from unittest import TestCase


class Test(TestCase):

    def setUp(self):
        from supermarket_crawler.spiders.park_n_shop import get_price
        self.func = get_price

    def test_return_none_if_input_is_none(self):
        self.assertIsNone(self.func(None))

    def test_input_must_be_string(self):
        self.assertRaises(AssertionError, self.func, float(123))

    def test_hkd_is_replaced(self):
        self.assertEqual(float(123), self.func("HK$123"))

    def test_thousand_separator_is_replaced(self):
        self.assertEqual(float(123456), self.func("123,456"))

    def test_decimal_places_are_kept(self):
        self.assertEqual(float(123.456), self.func("123.456"))
