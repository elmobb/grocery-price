import unittest
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from grocery_price import models
from grocery_price.cli.load import update_product_price_records
from grocery_price.items import Price


def scrapy_item(**kwargs):
    return Price(
        shop=kwargs.get("shop", "shop"),
        categories=kwargs.get("categories", "categories"),
        brand_name=kwargs.get("brand_name", "brand_name"),
        name=kwargs.get("name", "name"),
        price=kwargs.get("price", 1),
        currency=kwargs.get("currency", "currency"),
        rrp=kwargs.get("rrp", None),
        sku=kwargs.get("sku", "sku"),
        special_offers=kwargs.get("special_offers", "special_offers"),
        url=kwargs.get("url", "url"),
        others=kwargs.get("others", "others"),
        uom=kwargs.get("uom", "uom"),
        update_time=kwargs.get("update_time", datetime(2018, 1, 1)),
    )


class TestCase(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite:///:memory:")
        models.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()
        self.func = update_product_price_records

    def tearDown(self):
        self.session.close()

    def assertDatabaseRecords(self, products=None, prices=None):
        if products is not None:
            self.assertEqual(products, self.session.query(
                models.Product.shop,
                models.Product.sku,
                models.Product.update_time
            ).all())

        if prices is not None:
            self.assertEqual(prices, [(
                i.product.shop,
                i.product.sku,
                i.price,
                i.update_time
            ) for i in self.session.query(models.Price).all()])

    def test_do_not_allow_multiple_shops(self):
        self.assertRaises(AssertionError, self.func, session=self.session, items=[
            scrapy_item(shop="shop_0", sku="sku"),
            scrapy_item(shop="shop_1", sku="sku")
        ])

    def test_duplicated_items_will_be_removed_by_keeping_latest_one(self):
        self.func(session=self.session, items=[
            scrapy_item(sku="sku_0", update_time=datetime(2018, 1, 1, 0, 0, 1)),
            scrapy_item(sku="sku_0", update_time=datetime(2018, 1, 1, 0, 0, 3)),
            scrapy_item(sku="sku_0", update_time=datetime(2018, 1, 1, 0, 0, 2)),
            scrapy_item(sku="sku_1", update_time=datetime(2018, 1, 1, 0, 0, 0)),
        ])

        self.assertDatabaseRecords(
            products=[
                ("shop", "sku_0", datetime(2018, 1, 1, 0, 0, 3, 0)),
                ("shop", "sku_1", datetime(2018, 1, 1, 0, 0, 0, 0))
            ],
            prices=[
                ("shop", "sku_0", 1.0, datetime(2018, 1, 1, 0, 0, 3, 0)),
                ("shop", "sku_1", 1.0, datetime(2018, 1, 1, 0, 0, 0, 0))
            ]
        )

    def test_insert_one_new_product(self):
        self.func(session=self.session, items=[
            scrapy_item()
        ])

        self.assertDatabaseRecords(
            products=[
                ("shop", "sku", datetime(2018, 1, 1, 0, 0, 0, 0))
            ],
            prices=[
                ("shop", "sku", 1.0, datetime(2018, 1, 1, 0, 0, 0, 0))
            ]
        )

    def test_insert_multiple_new_products(self):
        self.func(session=self.session, items=[
            scrapy_item(sku="sku_1"),
            scrapy_item(sku="sku_2")
        ])

        self.assertDatabaseRecords(
            products=[
                ("shop", "sku_1", datetime(2018, 1, 1, 0, 0, 0, 0)),
                ("shop", "sku_2", datetime(2018, 1, 1, 0, 0, 0, 0))
            ],
            prices=[
                ("shop", "sku_1", 1.0, datetime(2018, 1, 1, 0, 0, 0, 0)),
                ("shop", "sku_2", 1.0, datetime(2018, 1, 1, 0, 0, 0, 0))
            ]
        )

    def test_update_one_product(self):
        self.func(session=self.session, items=[
            scrapy_item(sku="sku_1", update_time=datetime(2018, 1, 1)),
            scrapy_item(sku="sku_2", update_time=datetime(2018, 1, 1)),
            scrapy_item(sku="sku_3", update_time=datetime(2018, 1, 1))
        ])
        self.func(session=self.session, items=[
            scrapy_item(sku="sku_1", update_time=datetime(2018, 1, 2))
        ])

        self.assertDatabaseRecords(
            products=[
                ("shop", "sku_1", datetime(2018, 1, 2, 0, 0, 0, 0)),
                ("shop", "sku_2", datetime(2018, 1, 1, 0, 0, 0, 0)),
                ("shop", "sku_3", datetime(2018, 1, 1, 0, 0, 0, 0))
            ],
            prices=[
                ("shop", "sku_1", 1.0, datetime(2018, 1, 1, 0, 0, 0, 0)),
                ("shop", "sku_2", 1.0, datetime(2018, 1, 1, 0, 0, 0, 0)),
                ("shop", "sku_3", 1.0, datetime(2018, 1, 1, 0, 0, 0, 0)),
                ("shop", "sku_1", 1.0, datetime(2018, 1, 2, 0, 0, 0, 0))
            ]
        )

    def test_update_multiple_products(self):
        self.func(session=self.session, items=[
            scrapy_item(sku="sku_1", update_time=datetime(2018, 1, 1)),
            scrapy_item(sku="sku_2", update_time=datetime(2018, 1, 1)),
            scrapy_item(sku="sku_3", update_time=datetime(2018, 1, 1))
        ])
        self.func(session=self.session, items=[
            scrapy_item(sku="sku_1", update_time=datetime(2018, 1, 2)),
            scrapy_item(sku="sku_2", update_time=datetime(2018, 1, 2))
        ])

        self.assertDatabaseRecords(
            products=[
                ("shop", "sku_1", datetime(2018, 1, 2, 0, 0, 0, 0)),
                ("shop", "sku_2", datetime(2018, 1, 2, 0, 0, 0, 0)),
                ("shop", "sku_3", datetime(2018, 1, 1, 0, 0, 0, 0))
            ],
            prices=[
                ("shop", "sku_1", 1.0, datetime(2018, 1, 1, 0, 0, 0, 0)),
                ("shop", "sku_2", 1.0, datetime(2018, 1, 1, 0, 0, 0, 0)),
                ("shop", "sku_3", 1.0, datetime(2018, 1, 1, 0, 0, 0, 0)),
                ("shop", "sku_1", 1.0, datetime(2018, 1, 2, 0, 0, 0, 0)),
                ("shop", "sku_2", 1.0, datetime(2018, 1, 2, 0, 0, 0, 0)),
            ]
        )

    def test_update_products_in_same_batch(self):
        self.func(session=self.session, items=[
            scrapy_item(sku="sku_1", update_time=datetime(2018, 1, 1)),
            scrapy_item(sku="sku_2", update_time=datetime(2018, 1, 1)),
            scrapy_item(sku="sku_3", update_time=datetime(2018, 1, 1))
        ])
        self.func(session=self.session, items=[
            scrapy_item(sku="sku_1", update_time=datetime(2017, 12, 31)),
            scrapy_item(sku="sku_2", update_time=datetime(2018, 1, 2))
        ])

        self.assertDatabaseRecords(
            products=[
                ("shop", "sku_1", datetime(2018, 1, 1, 0, 0, 0, 0)),
                ("shop", "sku_2", datetime(2018, 1, 2, 0, 0, 0, 0)),
                ("shop", "sku_3", datetime(2018, 1, 1, 0, 0, 0, 0))
            ],
            prices=[
                ("shop", "sku_1", 1.0, datetime(2018, 1, 1, 0, 0, 0, 0)),
                ("shop", "sku_2", 1.0, datetime(2018, 1, 1, 0, 0, 0, 0)),
                ("shop", "sku_3", 1.0, datetime(2018, 1, 1, 0, 0, 0, 0)),
                ("shop", "sku_1", 1.0, datetime(2017, 12, 31, 0, 0, 0, 0)),
                ("shop", "sku_2", 1.0, datetime(2018, 1, 2, 0, 0, 0, 0))
            ]
        )

    def test_update_prices_of_same_update_time_and_of_same_price(self):
        self.func(session=self.session, items=[
            scrapy_item(sku="sku", update_time=datetime(2018, 1, 1), price=1)
        ])
        self.func(session=self.session, items=[
            scrapy_item(sku="sku", update_time=datetime(2018, 1, 1), price=1)
        ])

        self.assertDatabaseRecords(
            products=[
                ("shop", "sku", datetime(2018, 1, 1, 0, 0, 0, 0))
            ],
            prices=[
                ("shop", "sku", 1.0, datetime(2018, 1, 1, 0, 0, 0, 0))
            ]
        )
