import unittest
from datetime import date, datetime, timedelta

from app import db
from supermarket_crawler import models
from tests.test_app.test_resources.test_resources import TestResources


class Test(TestResources):
    def test_product_not_found(self):
        db.session.add(models.Product(shop="shop", sku="sku"))
        db.session.commit()

        response = self.client.get("/api/1/product/shop/unknown/stats")
        self.assert400(response)

    def test_output_format(self):
        db.session.add(models.Product(shop="shop", sku="sku", prices=[models.Price(
            price=1,
            update_time=datetime.now() - timedelta(days=i)
        ) for i in range(1000)]))
        db.session.commit()

        response = self.client.get("/api/1/product/shop/sku/stats")
        self.assertEqual([
            {
                "time_horizon_in_weeks": 0,
                "minimum_price":         float(1),
                "maximum_price":         float(1),
                "mode_prices":           [float(1)]
            },
            {
                "time_horizon_in_weeks": 1,
                "minimum_price":         float(1),
                "maximum_price":         float(1),
                "mode_prices":           [float(1)]
            },
            {
                "time_horizon_in_weeks": 2,
                "minimum_price":         float(1),
                "maximum_price":         float(1),
                "mode_prices":           [float(1)]
            },
            {
                "time_horizon_in_weeks": 4,
                "minimum_price":         float(1),
                "maximum_price":         float(1),
                "mode_prices":           [float(1)]
            },
            {
                "time_horizon_in_weeks": 13,
                "minimum_price":         float(1),
                "maximum_price":         float(1),
                "mode_prices":           [float(1)]
            },
            {
                "time_horizon_in_weeks": 26,
                "minimum_price":         float(1),
                "maximum_price":         float(1),
                "mode_prices":           [float(1)]
            },
            {
                "time_horizon_in_weeks": 52,
                "minimum_price":         float(1),
                "maximum_price":         float(1),
                "mode_prices":           [float(1)]
            }
        ], response.json)


class TestGetStats(unittest.TestCase):
    def setUp(self):
        from app.resources.stats import get_stats
        self.func = get_stats

    def test_no_available_prices(self):
        self.assertEqual({
            "minimum_price": None,
            "maximum_price": None,
            "mode_prices":   []
        }, self.func(prices=[], from_date=date(2018, 1, 1), to_date=date(2018, 1, 1)))

    def test_get_current_stats(self):
        self.assertEqual({
            "minimum_price": 3,
            "maximum_price": 3,
            "mode_prices":   [3]
        }, self.func(
            prices=[models.Price(price=price, update_time=update_time) for update_time, price in [
                (datetime(2018, 1, 1), 1),
                (datetime(2018, 1, 2), 2),
                (datetime(2018, 1, 3), 3)
            ]], from_date=date(2018, 1, 3), to_date=date(2018, 1, 3)))

    def test_get_last_week_stats(self):
        self.assertEqual({
            "minimum_price": 1,
            "maximum_price": 7,
            "mode_prices":   [1, 2, 3, 4, 5, 6, 7]
        }, self.func(
            prices=[models.Price(price=price, update_time=update_time) for update_time, price in [
                (datetime(2018, 1, 1), 1),
                (datetime(2018, 1, 2), 2),
                (datetime(2018, 1, 3), 3),
                (datetime(2018, 1, 4), 4),
                (datetime(2018, 1, 5), 5),
                (datetime(2018, 1, 6), 6),
                (datetime(2018, 1, 7), 7)
            ]], from_date=date(2018, 1, 1), to_date=date(2018, 1, 7)))

    def test_only_last_prices_of_each_days_are_considered_when_calculating_mode(self):
        self.assertEqual({
            "minimum_price": 1,
            "maximum_price": 100,
            "mode_prices":   [1, 2, 3, 4, 5, 6, 7]
        }, self.func(
            prices=[models.Price(price=price, update_time=update_time) for update_time, price in [
                (datetime(2018, 1, 1, 0, 0, 0), 100),
                (datetime(2018, 1, 1, 0, 0, 1), 1),
                (datetime(2018, 1, 2, 0, 0, 0), 100),
                (datetime(2018, 1, 2, 0, 0, 1), 2),
                (datetime(2018, 1, 3, 0, 0, 0), 100),
                (datetime(2018, 1, 3, 0, 0, 1), 3),
                (datetime(2018, 1, 4, 0, 0, 0), 100),
                (datetime(2018, 1, 4, 0, 0, 1), 4),
                (datetime(2018, 1, 5, 0, 0, 0), 100),
                (datetime(2018, 1, 5, 0, 0, 1), 5),
                (datetime(2018, 1, 6, 0, 0, 0), 100),
                (datetime(2018, 1, 6, 0, 0, 1), 6),
                (datetime(2018, 1, 7, 0, 0, 0), 100),
                (datetime(2018, 1, 7, 0, 0, 1), 7)
            ]], from_date=date(2018, 1, 1), to_date=date(2018, 1, 7)))

    def test_prices_outside_required_time_period_are_ignored(self):
        self.assertEqual({
            "minimum_price": 2,
            "maximum_price": 6,
            "mode_prices":   [2, 3, 4, 5, 6]
        }, self.func(
            prices=[models.Price(price=price, update_time=update_time) for update_time, price in [
                (datetime(2018, 1, 1), 1),
                (datetime(2018, 1, 2), 2),
                (datetime(2018, 1, 3), 3),
                (datetime(2018, 1, 4), 4),
                (datetime(2018, 1, 5), 5),
                (datetime(2018, 1, 6), 6),
                (datetime(2018, 1, 7), 7)
            ]], from_date=date(2018, 1, 2), to_date=date(2018, 1, 6)))
