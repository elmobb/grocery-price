BOT_NAME = "price"

SPIDER_MODULES = ["supermarket-crawler.spiders"]

FEED_FORMAT = "json"
FEED_EXPORT_INDENT = 4
FEED_EXPORT_ENCODING = "utf8"
FEED_URI = "test.json"

ITEM_PIPELINES = {
    "supermarket-crawler.item_pipelines.PricePipeline": 300
}
