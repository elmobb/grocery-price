from datetime import datetime

import scrapy

from ..items import Price


def get_price(price):
    if price is None:
        return None
    assert isinstance(price, str)
    for old, new in {
        "HK$": "",
        ",":   ""
    }.items():
        price = price.replace(old, new)
    return float(price)


class Spider(scrapy.Spider):
    name = "park_n_shop"
    start_urls_name = "PARK_N_SHOP_START_URLS"
    currency = "HKD"
    download_delay = 0

    def start_requests(self):
        for url in self.settings.get(self.start_urls_name).split("|"):
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        """
        @url http://www.parknshop.com/zh-hk/beverages-wine-spirits/lc/040000
        @returns items 36 36
        @returns requests 0 1
        """

        # Crawl next page.
        next_page = response.xpath("//div[@class='btn-show-more']")
        has_next_page = (next_page.xpath("@data-hasnextpage").extract_first() == "true")
        if has_next_page:
            next_page_url = next_page.xpath("@data-nextpageurl").extract_first()
            yield scrapy.Request(response.urljoin(next_page_url), callback=self.parse)

        # Crawl this page.
        for item in response.xpath("//*[@id='product-list']/div/div[2]/div[2]/div[2]/div"):
            yield Price(
                shop=self.name,
                categories=item.xpath(
                    ".//div[@class='homeProductCarousel']/@data-gtm-homeproductcarousel-category").extract_first(),
                brand_name=item.xpath(
                    ".//div[@class='homeProductCarousel']/@data-gtm-homeproductcarousel-brand").extract_first(),
                name=item.xpath(
                    ".//div[@class='homeProductCarousel']/@data-gtm-homeproductcarousel-name").extract_first(),
                price=get_price(price=item.xpath(".//div[@class='price discount']/text()").extract_first()),
                currency=self.currency,
                rrp=item.xpath(".//div[@class='price rrp']/span[1]/text()").extract_first(),
                sku=item.xpath(".//div[@class='favourite ']/@data-product-code").extract_first(),
                special_offers=item.xpath(".//div[@class='special-offer']/span[1]/text()").extract_first(),
                url=item.xpath(".//div[@class='name']/a[1]/@href").extract_first(),
                others=None,
                uom=item.xpath(".//span[@class='sizeUnit']/text()").extract_first(),
                update_time=datetime.now()
            )
