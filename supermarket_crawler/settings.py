BOT_NAME = "price"
COOKIES_ENABLED = False
DATABASE_URI = "sqlite:///temp.db"
DOWNLOAD_DELAY = 2
DOWNLOADER_MIDDLEWARES = {
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
    "scrapy_fake_useragent.middleware.RandomUserAgentMiddleware": 400,
}
EXTENSIONS = {
    "supermarket_crawler.extensions.StatsLogger": 500
}
FEED_FORMAT = "json"
FEED_EXPORT_INDENT = 4
FEED_EXPORT_ENCODING = "utf8"
FEED_URI = "test.json"
ITEM_PIPELINES = {
    "supermarket_crawler.item_pipelines.PricePipeline": 300
}
LOG_FILE = "log.txt"
SPIDER_MODULES = ["supermarket_crawler.spiders"]
