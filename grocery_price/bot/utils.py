import os
from datetime import date, timedelta

import pandas as pd
from sqlalchemy import or_

from grocery_price.models import Price, Product, get_session


def db_session(func):
    """Get a SQLAlchemy session and pass to the function. After getting function result, close the session.
    """

    def wrapper(*args, **kwargs):

        # Whether the session is created locally.
        is_local_session = "session" not in kwargs

        # Unit tests will pass session to function.
        if is_local_session:
            kwargs["session"] = get_session(uri=os.environ.get("DATABASE_URI"))

        result = func(*args, **kwargs)

        if is_local_session:
            kwargs["session"].close()

        return result

    return wrapper


@db_session
def find_products(session, keywords, shop=None, brand_name=None, name=None, uom=None):
    item_sets = []
    for keyword in keywords:
        query = session.query(Product).filter(or_(
            Product.brand_name.like(f"%{keyword}%"),
            Product.name.like(f"%{keyword}%")
        )).order_by(
            Product.shop,
            Product.brand_name,
            Product.name
        )

        if shop is not None:
            query = query.filter_by(shop=shop)

        if brand_name is not None:
            query = query.filter_by(brand_name=brand_name)

        if name is not None:
            query = query.filter_by(name=name)

        if uom is not None:
            query = query.filter_by(uom=uom)

        item_sets.append(set(query.all()))
    return list(set.intersection(*item_sets))


@db_session
def find_minimum_price(session, shop, sku, days=[0]):
    prices = pd.DataFrame(session.query(
        Price.update_time,
        Price.price
    ).join(
        Product
    ).filter(
        Product.shop == shop,
        Product.sku == sku
    ).filter(
        Price.update_time >= (date.today() - timedelta(days=max(days))).strftime("%Y-%m-%d")
    ).all(), columns=["update_time", "price"]).set_index("update_time").sort_index()["price"]

    def get_minimum_price_of_last_n_days(n):
        if len(prices) == 0:
            return None

        if n == 0:
            # Latest price.
            x = prices.loc[date.today():].values[-1]
        else:
            # Minimum price.
            x = prices.loc[(date.today() - timedelta(days=n - 1)).strftime("%Y-%m-%d"):].min()

        return x if pd.notnull(x) else None

    return {n: get_minimum_price_of_last_n_days(n) for n in days}
