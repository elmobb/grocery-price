from flask_restful import Api

from .price import Prices
from .product import Product, Products
from .stats import Stats

api = Api(prefix="/api/1")
api.add_resource(Products, "/products")
api.add_resource(Product, "/product/<string:shop>/<string:sku>")
api.add_resource(Prices, "/product/<string:shop>/<string:sku>/prices")
api.add_resource(Stats, "/product/<string:shop>/<string:sku>/stats")
