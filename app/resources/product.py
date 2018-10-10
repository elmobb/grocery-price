from flask_restful import Resource, abort, fields, marshal_with, reqparse
from sqlalchemy.orm.exc import NoResultFound

from supermarket_crawler.models import Product as db_Product

parser = reqparse.RequestParser()
parser.add_argument("sku")
parser.add_argument("shop")
parser.add_argument("brand")
parser.add_argument("name")
parser.add_argument("limit", default=10)

resource_fields = {
    "shop":        fields.String,
    "sku":         fields.String,
    "brand_name":  fields.String,
    "name":        fields.String,
    "uom":         fields.String,
    "url":         fields.String,
    "update_time": fields.DateTime(dt_format="iso8601")
}


class Products(Resource):
    @marshal_with(resource_fields)
    def get(self):
        args = parser.parse_args()
        query = db_Product.query

        if args["shop"] is not None:
            query = query.filter_by(shop=args["shop"])

        if args["sku"] is not None:
            query = query.filter_by(sku=args["sku"])

        if args["brand"] is not None:
            query = query.filter(db_Product.brand_name.like(f"%{args['brand']}%"))

        if args["name"] is not None:
            query = query.filter(db_Product.name.like(f"%{args['name']}%"))

        return query.order_by(db_Product.shop, db_Product.sku).limit(args["limit"]).all()


class Product(Resource):
    @marshal_with(resource_fields)
    def get(self, shop, sku):
        try:
            return db_Product.query.filter_by(shop=shop).filter_by(sku=sku).one()
        except NoResultFound:
            abort(400)
