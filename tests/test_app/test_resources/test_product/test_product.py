from app import db
from supermarket_crawler import models
from tests.test_app.test_resources.test_resources import TestResources


class Test(TestResources):
    def test_get(self):
        db.session.add_all([
            models.Product(shop="shop_1", sku="sku_1"),
            models.Product(shop="shop_2", sku="sku_2"),
            models.Product(shop="shop_3", sku="sku_3")
        ])
        db.session.commit()

        response = self.client.get("/api/1/product/shop_2/sku_2")
        self.assertEqual({
            "shop":        "shop_2",
            "sku":         "sku_2",
            "brand_name":  None,
            "name":        None,
            "uom":         None,
            "url":         None,
            "update_time": None
        }, response.json)

    def test_not_found(self):
        db.session.add_all([
            models.Product(shop="shop_1", sku="sku_1"),
            models.Product(shop="shop_2", sku="sku_2"),
            models.Product(shop="shop_3", sku="sku_3")
        ])
        db.session.commit()

        response = self.client.get("/api/1/product/shop_1/sku_2")
        self.assert400(response)
