from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.resources import api
from supermarket_crawler import models

db = SQLAlchemy(model_class=models.Base)


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    api.init_app(app)

    return app
