import json
from datetime import datetime

import requests
import scrapy

from ..items import Price


def get_start_urls(category_codes, page_size=60, page_type="searchResult"):
    """Get URLs that contain product details in JSON format.
    """
    assert isinstance(category_codes, list)
    assert all(isinstance(i, str) for i in category_codes)
    assert isinstance(page_size, int)
    assert page_type in ["searchResult"]

    urls = []
    for category_code in category_codes:
        def page_url(page):
            return f"https://www.hktvmall.com/hktv/zh/ajax/search_products?query=:relevance:street:main:category:{category_code}:&currentPage={page}&pageSize={page_size}&pageType={page_type}&categoryCode={category_code}"

        r = requests.get(url=page_url(page=0)).json()
        number_of_pages = r["pagination"]["numberOfPages"]
        urls.extend([page_url(page=n) for n in range(number_of_pages)])

    return urls


class Spider(scrapy.Spider):
    name = "hktvmall"
    start_urls = get_start_urls(category_codes=[
        ""
        "AA11080000000",  # 水果 蔬菜 鮮花
        "AA11110000000",  # 冷凍/急凍食品
        "AA11150000000",  # 零食 甜品
        "AA11220000000",  # 飲品 即沖飲品
        "AA11350000000",  # 即食麵 麵  意粉
        "AA11380000000",  # 米 食油
        "AA11450000000",  # 調味 醬料
        "AA11480000000",  # 湯 熟食 醃製食品
        "AA11550000000",  # 罐頭 乾貨
        "AA11600000000",  # 早餐 果醬
        "AA11650000000",  # 有機 健康食品
        "AA11720000000",  # 醫藥產品
        "AA11800000000",  # 紙品 即棄品 家居用品
        "AA11820000000",  # 家居清潔用品
        "AA11850000000",  # 個人護理用品
        "AA11920000000",  # 嬰兒用品 食品
        "AA11960000000"  # 貓狗用品
    ])
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
