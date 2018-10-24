BOT_NAME = "grocery_price"

SPIDER_MODULES = ["grocery_price.spiders"]
NEWSPIDER_MODULE = "grocery_price.spiders"

ROBOTSTXT_OBEY = True

DOWNLOAD_DELAY = 0

COOKIES_ENABLED = False

DOWNLOADER_MIDDLEWARES = {
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
    "scrapy_fake_useragent.middleware.RandomUserAgentMiddleware": 400,
}

EXTENSIONS = {
    "grocery_price.extensions.StatsLogger": 400
}

FEED_STORAGES = {
    "sftp": "scrapy_feedexporter_sftp.SFTPFeedStorage"
}

DATABASE_URI = "sqlite://"
