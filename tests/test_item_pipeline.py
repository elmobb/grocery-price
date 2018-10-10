import unittest
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from supermarket_crawler import models
from supermarket_crawler.item_pipelines import update_product_price_records
from supermarket_crawler.items import Price


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

    def test_update_product(self):
        # Prepare database.
        self.func(session=self.session, items=[
            scrapy_item(sku="sku_1", update_time=datetime(2018, 1, 1)),
            scrapy_item(sku="sku_2", update_time=datetime(2018, 1, 1)),
            scrapy_item(sku="sku_3", update_time=datetime(2018, 1, 1))
        ])

        self.func(session=self.session, items=[
            scrapy_item(sku="sku_1", update_time=datetime(2018, 1, 2))
        ])
        self.assertEqual(
            datetime(2018, 1, 2),
            self.session.query(models.Product).filter_by(sku="sku_1").one().update_time
        )
        self.assertEqual(
            datetime(2018, 1, 1),
            self.session.query(models.Product).filter_by(sku="sku_2").one().update_time
        )
        self.assertEqual(
            datetime(2018, 1, 1),
            self.session.query(models.Product).filter_by(sku="sku_3").one().update_time
        )
        self.assertEqual(3 + 1, len(self.session.query(models.Price).all()))

    def test_update_multiple_products(self):
        # Prepare database.
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
        self.assertEqual(3 + 2, len(self.session.query(models.Price).all()))

    def test_insert_new_prices_for_multiple_items(self):
        # Prepare database.
        self.func(session=self.session, items=[
            scrapy_item(sku="sku_1", update_time=datetime(2018, 1, 1)),
            scrapy_item(sku="sku_2", update_time=datetime(2018, 1, 1))
        ])

        self.func(session=self.session, items=[
            scrapy_item(sku="sku_1", update_time=datetime(2018, 1, 2)),
            scrapy_item(sku="sku_2", update_time=datetime(2018, 1, 2))
        ])
        self.assertEqual(2, len(self.session.query(models.Product).all()))
        self.assertEqual(2 + 2, len(self.session.query(models.Price).all()))

    def test_insert_same_item(self):
        self.func(session=self.session, items=[
            scrapy_item(update_time=datetime(2018, 1, 3)),
            scrapy_item(update_time=datetime(2018, 1, 1)),
            scrapy_item(update_time=datetime(2018, 1, 2))
        ])
        self.assertEqual(datetime(2018, 1, 3), self.session.query(models.Product).one().update_time)
        self.assertEqual(1, len(self.session.query(models.Price).all()))
