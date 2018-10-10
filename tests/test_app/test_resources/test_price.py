from datetime import datetime, timedelta

from app import db
from supermarket_crawler import models
from tests.test_app.test_resources.test_resources import TestResources


class Test(TestResources):
    def test_product_not_found(self):
        db.session.add_all([
            models.Product(shop="shop", sku="sku_1"),
            models.Product(shop="shop", sku="sku_2"),
            models.Product(shop="shop", sku="sku_3")
        ])
        db.session.commit()

        response = self.client.get("/api/1/product/shop/unknown_sku/prices")
        self.assert400(response)

    def test_get(self):
        db.session.add_all([
            models.Product(shop="shop", sku="sku_1"),
            models.Product(shop="shop", sku="sku_2", prices=[
                models.Price(price=1, currency="curr_1", update_time=datetime(2018, 1, 1))
            ]),
            models.Product(shop="shop", sku="sku_3", prices=[
                models.Price(price=2, currency="curr_2", update_time=datetime(2018, 1, 2)),
                models.Price(price=3, currency="curr_3", update_time=datetime(2018, 1, 3))
            ])
        ])
        db.session.commit()

        # No prices.
        response = self.client.get("/api/1/product/shop/sku_1/prices")
        self.assertEqual([], response.json)

        # 1 price.
        response = self.client.get("/api/1/product/shop/sku_2/prices")
        self.assertEqual([
            {
                "price":       1.0,
                "currency":    "curr_1",
                "update_time": "2018-01-01T00:00:00",
            }
        ], response.json)

        # Multiple prices.
        response = self.client.get("/api/1/product/shop/sku_3/prices")
        self.assertEqual([
            {
                "price":       3.0,
                "currency":    "curr_3",
                "update_time": "2018-01-03T00:00:00",
            },
            {
                "price":       2.0,
                "currency":    "curr_2",
                "update_time": "2018-01-02T00:00:00",
            }
        ], response.json)

    def test_prices_are_sorted_by_updated_time_in_descending_order(self):
        db.session.add_all([
            models.Product(shop="shop", sku="sku", prices=[
                models.Price(price=2, currency="curr_2", update_time=datetime(2018, 1, 2)),
                models.Price(price=3, currency="curr_3", update_time=datetime(2018, 1, 3)),
                models.Price(price=1, currency="curr_1", update_time=datetime(2018, 1, 1))
            ])
        ])
        db.session.commit()

        response = self.client.get("/api/1/product/shop/sku/prices")
        self.assertEqual([
            {
                "price":       3.0,
                "currency":    "curr_3",
                "update_time": "2018-01-03T00:00:00",
            },
            {
                "price":       2.0,
                "currency":    "curr_2",
                "update_time": "2018-01-02T00:00:00",
            },
            {
                "price":       1.0,
                "currency":    "curr_1",
                "update_time": "2018-01-01T00:00:00",
            }
        ], response.json)

    def test_get_with_limit(self):
        db.session.add_all([
            models.Product(shop="shop", sku="sku", prices=[
                models.Price(price=i, currency="curr", update_time=datetime(2018, 1, 1) + timedelta(days=i)) for i in
                range(100)])
        ])
        db.session.commit()

        complte_result = sorted([
            {
                "price":       float(i),
                "currency":    "curr",
                "update_time": (datetime(2018, 1, 1) + timedelta(days=i)).isoformat(),
            }
            for i in range(100)], key=lambda i: i["update_time"], reverse=True)

        default_limit = 7

        # Without limits.
        response = self.client.get("/api/1/product/shop/sku/prices")
        self.assertEqual(complte_result[:default_limit], response.json)

        # With smaller than default limit.
        response = self.client.get("/api/1/product/shop/sku/prices?limit=3")
        self.assertEqual(complte_result[:3], response.json)

        # With greater than default limit.
        response = self.client.get("/api/1/product/shop/sku/prices?limit=10")
        self.assertEqual(complte_result[:10], response.json)
