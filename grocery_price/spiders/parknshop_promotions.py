from datetime import datetime

import scrapy

from ..items import Promotion


def promotion_page_url(promotion_code):
    return f"https://www.parknshop.com/zh-hk/promotioncategory?q=:allPromotionCodes:allPromotionCodes:{promotion_code}"


class Spider(scrapy.Spider):
    name = "park_n_shop_promotions"
    start_urls = [
        promotion_page_url(promotion_code=i) for i in range(200000)  # As of 2018-11-02, there are 154887 codes.
    ]

    def parse(self, response):
        promotion_name = response.xpath(
            "//*[@id='product-list']/div/div[2]/div[2]/form/div/div[1]/h1/text()").extract_first().strip()

        # Skip if promotion name is missing. Mostly it is a dummy promotion code.
        if promotion_name is not None and promotion_name != "":

            # Crawl next page.
            next_page = response.xpath("//div[@class='btn-show-more']")
            has_next_page = (next_page.xpath("@data-hasnextpage").extract_first() == "true")
            if has_next_page:
                next_page_url = next_page.xpath("@data-nextpageurl").extract_first()
                yield scrapy.Request(response.urljoin(next_page_url), callback=self.parse)

            # Crawl this page.
            for item in response.xpath("//*[@id='product-list']/div/div[2]/div[2]/div[2]/div"):
                yield Promotion(
                    shop="park_n_shop",
                    code=response.request.url,
                    name=promotion_name,
                    sku=item.xpath(".//div[@class='favourite ']/@data-product-code").extract_first(),
                    update_time=datetime.now()
                )
