import logging

from models import get_session
from utils.load_item_files import update_product_price_records


class DatabasePipeline(object):
    def __init__(self):
        super(DatabasePipeline, self).__init__()
        self.items = []

    def close_spider(self, spider):
        session = get_session(uri=spider.crawler.settings["DATABASE_URI"])
        update_product_price_records(session, items=self.items)
        session.close()

    def process_item(self, item, spider):
        logging.info(f"crawled item# {len(self.items) + 1}: '{item['shop']}' '{item['name']}'")
        self.items.append(item)
        return item
