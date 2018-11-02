import scrapy


class Price(scrapy.Item):
    shop = scrapy.Field()
    categories = scrapy.Field()
    brand_name = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    currency = scrapy.Field()
    rrp = scrapy.Field()
    sku = scrapy.Field()
    special_offers = scrapy.Field()
    url = scrapy.Field()
    others = scrapy.Field()
    uom = scrapy.Field()
    update_time = scrapy.Field()


class Promotion(scrapy.Item):
    shop = scrapy.Field()
    promotion_name = scrapy.Field()
    sku = scrapy.Field()
    update_time = scrapy.Field()
