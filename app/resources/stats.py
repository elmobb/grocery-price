from datetime import datetime, timedelta

import pandas as pd
from flask_restful import Resource, abort, fields, marshal_with
from sqlalchemy.orm.exc import NoResultFound

from supermarket_crawler.models import Price as db_Price, Product as db_Product

resource_fields = {
    "time_horizon_in_weeks": fields.Integer,
    "minimum_price":         fields.Float,
    "maximum_price":         fields.Float,
    "mode_prices":           fields.List(fields.Float)
}


def get_stats(prices, from_date, to_date):
    df = pd.DataFrame([(i.update_time, i.price) for i in prices], columns=["update_time", "price"])

    df["update_date"] = df["update_time"].apply(lambda x: x.date())
    df["update_time"] = df["update_time"].apply(lambda x: x.time())

    df = df[(from_date <= df["update_date"]) & (df["update_date"] <= to_date)]

    return {
        "minimum_price": None if pd.isnull(df["price"].min()) else df["price"].min(),
        "maximum_price": None if pd.isnull(df["price"].max()) else df["price"].max(),
        "mode_prices":   df[df.groupby("update_date")["update_time"].transform(max) == df["update_time"]][
                             "price"].mode().tolist()
    }


class Stats(Resource):
    @marshal_with(resource_fields)
    def get(self, shop, sku):

        # Check if the requested product exists.
        try:
            db_Product.query.filter_by(shop=shop, sku=sku).one()
        except NoResultFound:
            abort(400)

        return [{
            "time_horizon_in_weeks": i,
            **get_stats(
                prices=db_Price.query.filter(db_Product.shop == shop, db_Product.sku == sku, db_Price.update_time >= (
                        datetime.now() - timedelta(days=52 * 7)).date()).all(),
                from_date=(datetime.now() - timedelta(days=i * 7)).date(),
                to_date=datetime.now().date()
            )
        } for i in [0, 1, 2, 4, 13, 26, 52]]
