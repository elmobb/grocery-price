from datetime import datetime

from app import db
from supermarket_crawler import models
from tests.test_app.test_resources.test_resources import TestResources


class Test(TestResources):
    def test_query_by_sku(self):
        db.session.add_all([
            models.Product(shop="shop_1", sku="sku_1"),
            models.Product(shop="shop_1", sku="sku_2"),
            models.Product(shop="shop_2", sku="sku_2")
        ])
        db.session.commit()

        # No items found.
        response = self.client.get("/api/1/products?sku=sku_0")
        self.assertEqual([], response.json)

        # 1 item found.
        response = self.client.get("/api/1/products?sku=sku_1")
        self.assertEqual([
            {
                "shop":        "shop_1",
                "sku":         "sku_1",
                "brand_name":  None,
                "name":        None,
                "uom":         None,
                "url":         None,
                "update_time": None
            }
        ], response.json)

        # Multiple items found.
        response = self.client.get("/api/1/products?sku=sku_2")
        self.assertEqual([
            {
                "shop":        "shop_1",
                "sku":         "sku_2",
                "brand_name":  None,
                "name":        None,
                "uom":         None,
                "url":         None,
                "update_time": None
            },
            {
                "shop":        "shop_2",
                "sku":         "sku_2",
                "brand_name":  None,
                "name":        None,
                "uom":         None,
                "url":         None,
                "update_time": None
            }
        ], response.json)

    def test_query_by_shop(self):
        db.session.add_all([
            models.Product(shop="shop_1", sku="sku_1"),
            models.Product(shop="shop_2", sku="sku_1"),
            models.Product(shop="shop_2", sku="sku_2")
        ])
        db.session.commit()

        # No items found.
        response = self.client.get("/api/1/products?shop=shop_0")
        self.assertEqual([], response.json)

        # 1 item found.
        response = self.client.get("/api/1/products?shop=shop_1")
        self.assertEqual([
            {
                "shop":        "shop_1",
                "sku":         "sku_1",
                "brand_name":  None,
                "name":        None,
                "uom":         None,
                "url":         None,
                "update_time": None
            }
        ], response.json)

        # Multiple items found.
        response = self.client.get("/api/1/products?shop=shop_2")
        self.assertEqual([
            {
                "shop":        "shop_2",
                "sku":         "sku_1",
                "brand_name":  None,
                "name":        None,
                "uom":         None,
                "url":         None,
                "update_time": None
            },
            {
                "shop":        "shop_2",
                "sku":         "sku_2",
                "brand_name":  None,
                "name":        None,
                "uom":         None,
                "url":         None,
                "update_time": None
            }
        ], response.json)

    def test_query_by_brand_name(self):
        db.session.add_all([
            models.Product(shop="shop_1", sku="sku_1", brand_name="brand_1"),
            models.Product(shop="shop_2", sku="sku_2", brand_name="brand_2"),
            models.Product(shop="shop_3", sku="sku_3", brand_name="brand_3")
        ])
        db.session.commit()

        # No items found.
        response = self.client.get("/api/1/products?brand=0")
        self.assertEqual([], response.json)

        # 1 item found.
        response = self.client.get("/api/1/products?brand=2")
        self.assertEqual([
            {
                "shop":        "shop_2",
                "sku":         "sku_2",
                "brand_name":  "brand_2",
                "name":        None,
                "uom":         None,
                "url":         None,
                "update_time": None
            }
        ], response.json)

        # Multiple items found.
        response = self.client.get("/api/1/products?brand=a")
        self.assertEqual([
            {
                "shop":        "shop_1",
                "sku":         "sku_1",
                "brand_name":  "brand_1",
                "name":        None,
                "uom":         None,
                "url":         None,
                "update_time": None
            },
            {
                "shop":        "shop_2",
                "sku":         "sku_2",
                "brand_name":  "brand_2",
                "name":        None,
                "uom":         None,
                "url":         None,
                "update_time": None
            },
            {
                "shop":        "shop_3",
                "sku":         "sku_3",
                "brand_name":  "brand_3",
                "name":        None,
                "uom":         None,
                "url":         None,
                "update_time": None
            }
        ], response.json)

    def test_query_by_name(self):
        db.session.add_all([
            models.Product(shop="shop_1", sku="sku_1", name="name_1"),
            models.Product(shop="shop_2", sku="sku_2", name="name_2"),
            models.Product(shop="shop_3", sku="sku_3", name="name_3")
        ])
        db.session.commit()

        # No items found.
        response = self.client.get("/api/1/products?name=0")
        self.assertEqual([], response.json)

        # 1 item found.
        response = self.client.get("/api/1/products?name=2")
        self.assertEqual([
            {
                "shop":        "shop_2",
                "sku":         "sku_2",
                "brand_name":  None,
                "name":        "name_2",
                "uom":         None,
                "url":         None,
                "update_time": None
            }
        ], response.json)

        # Multiple items found.
        response = self.client.get("/api/1/products?name=a")
        self.assertEqual([
            {
                "shop":        "shop_1",
                "sku":         "sku_1",
                "brand_name":  None,
                "name":        "name_1",
                "uom":         None,
                "url":         None,
                "update_time": None
            },
            {
                "shop":        "shop_2",
                "sku":         "sku_2",
                "brand_name":  None,
                "name":        "name_2",
                "uom":         None,
                "url":         None,
                "update_time": None
            },
            {
                "shop":        "shop_3",
                "sku":         "sku_3",
                "brand_name":  None,
                "name":        "name_3",
                "uom":         None,
                "url":         None,
                "update_time": None
            }
        ], response.json)

    def test_products_are_sorted_by_shop_and_sku(self):
        db.session.add_all([
            models.Product(shop="shop_2", sku="sku_1"),
            models.Product(shop="shop_1", sku="sku_2"),
            models.Product(shop="shop_2", sku="sku_3")
        ])
        db.session.commit()

        response = self.client.get("/api/1/products")
        self.assertEqual([
            {
                "shop":        "shop_1",
                "sku":         "sku_2",
                "brand_name":  None,
                "name":        None,
                "uom":         None,
                "url":         None,
                "update_time": None
            },
            {
                "shop":        "shop_2",
                "sku":         "sku_1",
                "brand_name":  None,
                "name":        None,
                "uom":         None,
                "url":         None,
                "update_time": None
            },
            {
                "shop":        "shop_2",
                "sku":         "sku_3",
                "brand_name":  None,
                "name":        None,
                "uom":         None,
                "url":         None,
                "update_time": None
            }
        ], response.json)

    def test_get_with_limit(self):
        db.session.add_all([models.Product(shop="shop_1", sku=f"sku_{str(i).zfill(2)}") for i in range(100)])
        db.session.commit()

        response = self.client.get("/api/1/products?limit=2")
        self.assertEqual([
            {
                "shop":        "shop_1",
                "sku":         "sku_00",
                "brand_name":  None,
                "name":        None,
                "uom":         None,
                "url":         None,
                "update_time": None
            },
            {
                "shop":        "shop_1",
                "sku":         "sku_01",
                "brand_name":  None,
                "name":        None,
                "uom":         None,
                "url":         None,
                "update_time": None
            }
        ], response.json)

    def test_get_with_default_limit(self):
        db.session.add_all([models.Product(shop="shop_1", sku=f"sku_{str(i).zfill(2)}") for i in range(100)])
        db.session.commit()

        default_limit = 10

        response = self.client.get("/api/1/products")
        self.assertEqual([
            {
                "shop":        "shop_1",
                "sku":         f"sku_{str(i).zfill(2)}",
                "brand_name":  None,
                "name":        None,
                "uom":         None,
                "url":         None,
                "update_time": None
            } for i in range(default_limit)
        ], response.json)

    def test_update_time_is_in_iso_format(self):
        db.session.add_all([
            models.Product(shop="shop_1", sku="sku_1"),
            models.Product(shop="shop_2", sku="sku_2", update_time=datetime(2018, 1, 1)),
            models.Product(shop="shop_3", sku="sku_3", update_time=datetime(2018, 1, 1, 1, 1, 1))
        ])
        db.session.commit()

        response = self.client.get("/api/1/products")
        self.assertEqual([
            {
                "shop":        "shop_1",
                "sku":         "sku_1",
                "brand_name":  None,
                "name":        None,
                "uom":         None,
                "url":         None,
                "update_time": None
            },
            {
                "shop":        "shop_2",
                "sku":         "sku_2",
                "brand_name":  None,
                "name":        None,
                "uom":         None,
                "url":         None,
                "update_time": "2018-01-01T00:00:00"
            },
            {
                "shop":        "shop_3",
                "sku":         "sku_3",
                "brand_name":  None,
                "name":        None,
                "uom":         None,
                "url":         None,
                "update_time": "2018-01-01T01:01:01"
            }
        ], response.json)
