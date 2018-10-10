from flask_restful import Resource, abort, fields, marshal_with, reqparse
from sqlalchemy.orm.exc import NoResultFound

from supermarket_crawler.models import Price as db_Price, Product as db_Product

parser = reqparse.RequestParser()
parser.add_argument("limit", default=7)

resource_fields = {
    "price":       fields.Float,
    "currency":    fields.String,
    "update_time": fields.DateTime(dt_format="iso8601")
}


class Prices(Resource):
    @marshal_with(resource_fields)
    def get(self, shop, sku):
        args = parser.parse_args()

        # Check if the requested product exists.
        try:
            db_Product.query.filter_by(shop=shop, sku=sku).one()
        except NoResultFound:
            abort(400)

        return db_Price.query.join(db_Product).filter(db_Product.shop == shop, db_Product.sku == sku).order_by(
            db_Price.update_time.desc()).limit(args["limit"]).all()
