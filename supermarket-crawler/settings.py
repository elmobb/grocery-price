BOT_NAME = "price"

SPIDER_MODULES = ["supermarket-crawler.spiders"]

FEED_FORMAT = "json"
FEED_EXPORT_INDENT = 4
FEED_EXPORT_ENCODING = "utf8"
FEED_URI = "test.json"

ITEM_PIPELINES = {
    "supermarket-crawler.item_pipelines.PricePipeline": 300
}

DOWNLOADER_MIDDLEWARES = {
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
    "scrapy_fake_useragent.middleware.RandomUserAgentMiddleware": 400,
}

COOKIES_ENABLED = False
DOWNLOAD_DELAY = 2

LOG_FILE = "log.txt"

EXTENSIONS = {
    "supermarket-crawler.extensions.StatsLogger": 500
}
