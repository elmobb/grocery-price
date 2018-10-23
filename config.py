import os


class Config(object):
    DATABASE_URI = os.environ.get("DATABASE_URI")
    FEED_URI = os.environ.get("FEED_URI")
    SCRAPY_API_KEY = os.environ.get("SCRAPY_API_KEY")
    SCRAPY_PROJECT_ID = os.environ.get("SCRAPY_PROJECT_ID")
    TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
