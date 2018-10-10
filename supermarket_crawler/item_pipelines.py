import logging

from .models import Product, Price, get_session


def update_product_price_records(session, items):
    # Preload all existing products for better performance.
    existing_products = {(i.shop, i.sku): i for i in session.query(Product).filter_by().all()}

    new_products = []
    seen_keys = set()

    # For duplicated items, keep only the latest updated one.
    for item in sorted(items, key=lambda i: i["update_time"], reverse=True):

        if (item["shop"], item["sku"]) in seen_keys:
            continue

        seen_keys.add((item["shop"], item["sku"]))

        product = existing_products.get((item["shop"], item["sku"]))

        if product is not None:
            # Update record.
            product.shop = item["shop"]
            product.sku = item["sku"]
            product.brand_name = item["brand_name"]
            product.name = item["name"]
            product.uom = item["uom"]
            product.url = item["url"]
            product.update_time = item["update_time"]
        else:
            # Insert record.
            product = Product(
                shop=item["shop"],
                sku=item["sku"],
                brand_name=item["brand_name"],
                name=item["name"],
                uom=item["uom"],
                url=item["url"],
                update_time=item["update_time"]
            )
            new_products.append(product)

        # Add new price record.
        product.prices.append(Price(
            price=item["price"],
            currency=item["currency"],
            update_time=item["update_time"]
        ))

    session.add_all(new_products)
    session.commit()


class DatabasePipeline(object):

    def __init__(self):
        super(DatabasePipeline, self).__init__()
        self.items = []

    def close_spider(self, spider):
        session = get_session(spider=spider)
        update_product_price_records(session, items=self.items)
        session.close()

    def process_item(self, item, spider):
        logging.info(f"crawled item# {len(self.items) + 1}: '{item['shop']}' '{item['name']}'")
        self.items.append(item)
        return item
