from datetime import datetime
import scrapy

from ..items import Price


class Spider(scrapy.Spider):
    name = "park_n_shop"
    start_urls = ["http://www.parknshop.com/zh-hk"]

    def parse(self, response):
        """
        @url http://www.parknshop.com/zh-hk
        @returns items 0 0
        @returns requests 0
        """
        for category in response.xpath("//div[@class='list lv1']/a/@href").extract():
            yield scrapy.Request(response.urljoin(category), callback=self.parse_category_items)

    def parse_category_items(self, response):
        """
        @url http://www.parknshop.com/zh-hk/beverages-wine-spirits/lc/040000
        @returns items 0 0
        @returns requests 0
        """
        for item in response.xpath("//div[@class='photo']/a/@href").extract():
            yield scrapy.Request(response.urljoin(item), callback=self.parse_item)

        next_page = response.xpath(
            "//*[@id='product-list']//*[contains(@data-hasnextpage, 'true')]/@data-nextpageurl").extract_first()
        yield scrapy.Request(response.urljoin(next_page), callback=self.parse_category_items)

    def parse_item(self, response):
        """
        @url http://www.parknshop.com/zh-hk/greek-style-blueberry-yogurt/p/BP_448916
        @returns items 1 1
        @returns requests 0 0
        @scrapes shop categories brand_name name price currency rrp sku special_offers url others uom update_time
        """
        yield Price(
            shop=self.name,
            categories=response.xpath("//*[@id='breadcrumb']//*[@itemprop='name']/text()").extract()[1:-1],
            brand_name=response.xpath("//*[@id='item-photo-container']/div[1]/a/span/text()").extract_first(),
            name=response.xpath("//h1[@class='productName productNameForH1']/text()").extract_first(),
            price=float(
                response.xpath("//*[@id='item-photo-container']//*[@itemprop='price']/@content").extract_first()),
            currency=response.xpath(
                "//*[@id='item-photo-container']//*[@itemprop='priceCurrency']/@content").extract_first(),
            rrp=response.xpath(
                "//*[@id='item-photo-container']/div[3]/div[3]/div[1]/div/span[2]/span/text()").extract_first(),
            sku=str(response.xpath("//*[@id='item-photo-container']/div[2]/div[2]/div[1]/span/text()").extract_first()),
            special_offers=response.xpath("//*[@id='special-offers']/div[2]/div//*[@class='info']/text()").extract(),
            url=response.url,
            others=response.xpath("//*[@class='desktop-others-customer left']/li/div/@title").extract(),
            uom=response.xpath("//*[@id='item-photo-container']/div[1]/span/text()").extract_first(),
            update_time=datetime.now()
        )
