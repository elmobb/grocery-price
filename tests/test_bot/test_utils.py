import unittest
from datetime import date, datetime, time, timedelta

from grocery_price.models import Price, Product, get_session


class TestFindProduct(unittest.TestCase):
    def setUp(self):
        from grocery_price.bot.utils import find_products
        self.func = find_products
        self.session = get_session(uri="sqlite://")

    def tearDown(self):
        self.session.close()

    def test_keywords_will_be_searched_in_brand_name_and_product_name(self):
        products = [
            Product(shop="shop", sku="sku_0", brand_name="xxxxxxxxx", name="xxxxxxxxx"),
            Product(shop="shop", sku="sku_1", brand_name="keyword_1", name="xxxxxxxxx"),
            Product(shop="shop", sku="sku_2", brand_name="xxxxxxxxx", name="keyword_1"),
            Product(shop="shop", sku="sku_3", brand_name="keyword_1", name="keyword_1"),
            Product(shop="shop", sku="sku_4", brand_name="___keyword_1___", name="xxxxxxxxx")  # Wildcard search.
        ]
        self.session.add_all(products)
        self.session.commit()
        self.assertCountEqual([
            products[1],
            products[2],
            products[3],
            products[4]
        ], self.func(keywords=["keyword_1"], session=self.session))

    def test_all_keywords_must_be_found(self):
        products = [
            Product(shop="shop", sku="sku_0", brand_name="xxxxxxxxx ", name="xxxxxxxxx"),
            Product(shop="shop", sku="sku_1", brand_name="keyword_1", name="xxxxxxxxx"),
            Product(shop="shop", sku="sku_2", brand_name="xxxxxxxxx", name="keyword_1"),
            Product(shop="shop", sku="sku_3", brand_name="keyword_2", name="xxxxxxxxx"),
            Product(shop="shop", sku="sku_4", brand_name="xxxxxxxxx", name="keyword_2"),
            Product(shop="shop", sku="sku_5", brand_name="keyword_1", name="keyword_2"),
            Product(shop="shop", sku="sku_6", brand_name="keyword_2", name="keyword_1"),
            Product(shop="shop", sku="sku_7", brand_name="keyword_1_keyword_2", name="xxxxxxxxxxx"),
            Product(shop="shop", sku="sku_8", brand_name="keyword_2_keyword_1", name="xxxxxxxxxxx")  # Inverse order.
        ]
        self.session.add_all(products)
        self.session.commit()
        self.assertCountEqual([
            products[5],
            products[6],
            products[7],
            products[8]
        ], self.func(keywords=["keyword_1", "keyword_2"], session=self.session))

    def test_search_by_multiple_criteria(self):
        products = [
            Product(shop="shop", sku="sku", brand_name="brand_name", name="name", uom="uom"),
            Product(shop="xxxx", sku="sku", brand_name="brand_name", name="name", uom="uom"),
            Product(shop="shop", sku="xxx", brand_name="brand_name", name="name", uom="uom"),
            Product(shop="shop", sku="sku", brand_name="xxxxxxxxxx", name="name", uom="uom"),
            Product(shop="shop", sku="sku", brand_name="brand_name", name="xxxx", uom="uom"),
            Product(shop="shop", sku="sku", brand_name="brand_name", name="name", uom="xxx")
        ]
        self.session.add_all(products)
        self.session.commit()
        self.assertCountEqual([
            products[0],
            products[2]
        ], self.func(
            keywords=["name"],
            shop="shop",
            brand_name="brand_name",
            name="name",
            uom="uom",
            session=self.session
        ))


class TestFindMinimumPrice(unittest.TestCase):
    def setUp(self):
        from grocery_price.bot.utils import find_minimum_price
        self.func = find_minimum_price
        self.session = get_session(uri="sqlite://")

    def tearDown(self):
        self.session.close()

    def test_filter_by_shop_and_sku(self):
        self.session.add_all([
            Product(shop="shop_0", sku="sku_0", prices=[
                Price(price=2, update_time=datetime.now())
            ]),
            Product(shop="shop_0", sku="sku_1", prices=[
                Price(price=3, update_time=datetime.now())
            ]),
            Product(shop="shop_1", sku="sku_0", prices=[
                Price(price=1, update_time=datetime.now())
            ]),
        ])
        self.session.commit()
        self.assertEqual({
            0: float(2)
        }, self.func(shop="shop_0", sku="sku_0", days=[0], session=self.session))

    def test_only_consider_price_records_within_required_days(self):
        self.session.add_all([
            Product(shop="shop", sku="sku", prices=[
                Price(price=5, update_time=datetime.combine(date.today(), time(0, 2))),  # Latest
                Price(price=4, update_time=datetime.combine(date.today(), time(0, 1))),  # Early today
                Price(price=3, update_time=datetime.now() - timedelta(days=1)),  # Yesterday
                Price(price=2, update_time=datetime.now() - timedelta(days=2)),
                Price(price=1, update_time=datetime.now() - timedelta(days=3))
            ])
        ])
        self.session.commit()
        self.assertEqual({
            0: float(5),
            1: float(4),
            2: float(3),
            3: float(2),
            4: float(1)
        }, self.func(shop="shop", sku="sku", days=[0, 1, 2, 3, 4], session=self.session))

    def test_timezone_difference_is_considered(self):
        self.session.add_all([
            Product(shop="shop", sku="sku", prices=[
                Price(price=5, update_time=datetime.combine(date.today(), time(8, 0))),  # Still today after adjustment.
                Price(price=4, update_time=datetime.combine(date.today(), time(7, 59))),  # Become yesterday.
                Price(price=3, update_time=datetime.combine(date.today(), time(8, 0)) - timedelta(days=1)),
                Price(price=2, update_time=datetime.combine(date.today(), time(8, 0)) - timedelta(days=2)),
                Price(price=1, update_time=datetime.combine(date.today(), time(8, 0)) - timedelta(days=3))
            ])
        ])
        self.session.commit()
        self.assertEqual({
            0: float(5),
            1: float(5),
            2: float(3),
            3: float(2),
            4: float(1)
        }, self.func(shop="shop", sku="sku", days=[0, 1, 2, 3, 4], hours=8, session=self.session))

    def test_no_price_records_found(self):
        self.session.add_all([
            Product(shop="shop", sku="sku", prices=[])
        ])
        self.session.commit()
        self.assertEqual({
            0: None
        }, self.func(shop="shop", sku="sku", days=[0], session=self.session))
