from flask_restful import Api

from .product import Product, Products

api = Api(prefix="/api/1")
api.add_resource(Products, "/products")
api.add_resource(Product, "/product/<string:shop>/<string:sku>")
