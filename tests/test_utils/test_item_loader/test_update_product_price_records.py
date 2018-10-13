import unittest
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import models
from supermarket_crawler.items import Price
from utils.load_item_files import update_product_price_records


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

    def test_insert_one_new_product(self):
        self.func(session=self.session, items=[
            scrapy_item()
        ])

        self.assertEqual(1, len(self.session.query(models.Product).all()))
        self.assertEqual(1, len(self.session.query(models.Price).all()))

    def test_insert_multiple_new_products(self):
        self.func(session=self.session, items=[
            scrapy_item(sku="sku_1"),
            scrapy_item(sku="sku_2")
        ])

        self.assertEqual(2, len(self.session.query(models.Product).all()))
        self.assertEqual(2, len(self.session.query(models.Price).all()))

    def test_update_one_product(self):
        self.func(session=self.session, items=[
            scrapy_item(sku="sku_1", update_time=datetime(2018, 1, 1)),
            scrapy_item(sku="sku_2", update_time=datetime(2018, 1, 1)),
            scrapy_item(sku="sku_3", update_time=datetime(2018, 1, 1))
        ])

        self.func(session=self.session, items=[
            scrapy_item(sku="sku_1", update_time=datetime(2018, 1, 2))
        ])

        self.assertEqual([
            ("sku_1", datetime(2018, 1, 2)),
            ("sku_2", datetime(2018, 1, 1)),
            ("sku_3", datetime(2018, 1, 1))
        ], self.session.query(models.Product.sku, models.Product.update_time).all())

        self.assertEqual(4, len(self.session.query(models.Price).all()))

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

        self.assertEqual(
            datetime(2018, 1, 2),
            self.session.query(models.Product).filter_by(sku="sku_1").one().update_time
        )
        self.assertEqual(
            datetime(2018, 1, 2),
            self.session.query(models.Product).filter_by(sku="sku_2").one().update_time
        )
        self.assertEqual(
            datetime(2018, 1, 1),
            self.session.query(models.Product).filter_by(sku="sku_3").one().update_time
        )

        self.assertEqual([
            ("sku_1", datetime(2018, 1, 2)),
            ("sku_2", datetime(2018, 1, 2)),
            ("sku_3", datetime(2018, 1, 1))
        ], self.session.query(models.Product.sku, models.Product.update_time).all())
        self.assertEqual(5, len(self.session.query(models.Price).all()))

    def test_update_products_in_same_batch(self):
        self.func(session=self.session, items=[
            scrapy_item(sku="sku_1", update_time=datetime(2018, 1, 1)),
            scrapy_item(sku="sku_2", update_time=datetime(2018, 1, 1)),
            scrapy_item(sku="sku_3", update_time=datetime(2018, 1, 1)),
            scrapy_item(sku="sku_1", update_time=datetime(2017, 12, 31)),
            scrapy_item(sku="sku_2", update_time=datetime(2018, 1, 2))
        ])

        self.assertEqual([
            ("sku_1", datetime(2018, 1, 1)),
            ("sku_2", datetime(2018, 1, 2)),
            ("sku_3", datetime(2018, 1, 1))
        ], self.session.query(models.Product.sku, models.Product.update_time).all())
        self.assertEqual(5, len(self.session.query(models.Price).all()))

    def test_update_prices_of_same_update_time_and_of_same_price(self):
        self.func(session=self.session, items=[
            scrapy_item(sku="sku", update_time=datetime(2018, 1, 1), price=1),
            scrapy_item(sku="sku", update_time=datetime(2018, 1, 1), price=1)
        ])
        self.assertEqual([
            ("sku", datetime(2018, 1, 1))
        ], self.session.query(models.Product.sku, models.Product.update_time).all())
        self.assertEqual([
            (1, datetime(2018, 1, 1))
        ], self.session.query(models.Price.price, models.Price.update_time).all())

    def test_update_prices_of_same_update_time_and_of_different_prices(self):
        self.func(session=self.session, items=[
            scrapy_item(sku="sku", update_time=datetime(2018, 1, 1), price=1),
            scrapy_item(sku="sku", update_time=datetime(2018, 1, 1), price=2)
        ])
        self.assertEqual([
            ("sku", datetime(2018, 1, 1))
        ], self.session.query(models.Product.sku, models.Product.update_time).all())
        self.assertEqual([
            (1, datetime(2018, 1, 1))
        ], self.session.query(models.Price.price, models.Price.update_time).all())

    def test_microsecond_of_update_time_are_ignored(self):
        self.func(session=self.session, items=[
            scrapy_item(sku="sku", update_time=datetime(2018, 1, 1, 0, 0, 0, 1), price=1),
            scrapy_item(sku="sku", update_time=datetime(2018, 1, 1, 0, 0, 0, 2), price=2)
        ])
        self.assertEqual([
            ("sku", datetime(2018, 1, 1, 0, 0, 0, 2))
        ], self.session.query(models.Product.sku, models.Product.update_time).all())
        self.assertEqual([
            (2, datetime(2018, 1, 1, 0, 0, 0, 2))
        ], self.session.query(models.Price.price, models.Price.update_time).all())

    def test_commit_in_batches(self):
        self.func(session=self.session, items=[scrapy_item(sku=i) for i in range(100)], commit_frequency=10)
        self.assertEqual(100, self.session.query(models.Product).count())
