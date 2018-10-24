import json
from datetime import datetime

import requests
import scrapy

from ..items import Price


def get_page_urls(category_code, page_size=60, page_type="searchResult"):
    """Get URLs that contain product details in JSON format.
    """
    assert isinstance(category_code, str)
    assert all(isinstance(i, str) for i in category_code)
    assert isinstance(page_size, int)
    assert page_type in ["searchResult"]

    def get_page_url(current_page):
        return f"https://www.hktvmall.com/hktv/zh/ajax/search_products?query=:relevance:street:main:category:{category_code}:&currentPage={current_page}&pageSize={page_size}&pageType={page_type}&categoryCode={category_code}"

    r = requests.get(url=get_page_url(current_page=0)).json()
    number_of_pages = r["pagination"]["numberOfPages"]

    return [get_page_url(current_page=n) for n in range(number_of_pages)]


class Spider(scrapy.Spider):
    name = "hktvmall"
    start_urls = get_page_urls(category_code="AA11220000000")
    currency = "HKD"

    def parse(self, response):
        """
        @url https://www.hktvmall.com/hktv/zh/ajax/search_products?query=:relevance:street:main:category:AA11220000000:&currentPage=0&pageSize=60&pageType=searchResult&categoryCode=AA11220000000
        @returns items 60 60
        @returns requests 0 1
        """
        json_response = json.loads(response.body_as_unicode())
        for product in json_response["products"]:

            # If there is no discounted prices, price is stored in "price" key.
            # If there is discounted price, RRP and discounted price are stored in "price" and "promotionPrice" keys.
            promotion_price = product.get("promotionPrice")
            price = product.get("price")
            has_discount_price = promotion_price is not None

            categories = product.get("categories")

            yield Price(
                shop=self.name,
                categories="|".join([i.get("name") for i in categories]) if categories is not None else None,
                brand_name=product.get("brandName"),
                name=product.get("summary"),
                price=promotion_price.get("value") if has_discount_price else price.get("value"),
                currency=product.get("price").get("currencyIso"),
                rrp=price.get("value"),
                sku=product.get("code"),
                special_offers=None,
                url=product.get("url"),
                others=None,
                uom=product.get("packingSpec"),
                update_time=datetime.now()
            )
