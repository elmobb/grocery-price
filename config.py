import os


class Config(object):
    DATABASE_URI = os.environ.get("DATABASE_URI")
    FEED_URI = os.environ.get("FEED_URI")
    SCRAPY_API_KEY = os.environ.get("SCRAPY_API_KEY")
