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
START_URLS = {
    "park_n_shop": [
        "https://www.parknshop.com/zh-hk/beverages-wine-spirits/lc/040000",
        "https://www.parknshop.com/en/groceries/lc/020000",
        "https://www.parknshop.com/en/biscuits-snacks-confectionery/lc/030000",
        "https://www.parknshop.com/zh-hk/household/lc/200000",
        "https://www.parknshop.com/zh-hk/baby-care/lc/080000",
        "https://www.parknshop.com/zh-hk/health-beauty-care/lc/090000",
        "https://www.parknshop.com/zh-hk/frozen-food/lc/060000",
        "https://www.parknshop.com/zh-hk/fresh-food/lc/070000"
        "https://www.parknshop.com/zh-hk/breakfast-bakery/lc/010000",
        "https://www.parknshop.com/zh-hk/dairy-chilled-eggs/lc/050000",
        "https://www.parknshop.com/zh-hk/pet-care/lc/210000"
    ]
}
SPIDER_MODULES = ["supermarket_crawler.spiders"]
