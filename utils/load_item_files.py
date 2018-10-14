import json
import logging
import os
from datetime import datetime

from models import Price, Product, get_session as get_db_session
from utils.sftp import get_session as get_sftp_session

logging.getLogger().setLevel(logging.INFO)


def update_product_price_records(session, items, commit_frequency=1000):
    """Upload Scrapy price items to database.

    Only the latest product details will be kept. All price records will be kept.
    Uploading same set of items in 1 or multiple batches should have the same result.
    """
    existing_products = {(i.shop, i.sku): i for i in session.query(Product).filter_by().all()}
    new_products = []

    # Ensure the latest version of product is updated first.
    for i, item in enumerate(sorted(items, key=lambda i: i["update_time"], reverse=True)):

        item = clean_item(item=item)

        logging.info(
            f"Processing item {i + 1}/{len(items)} ({round((i+1)/len(items)*100,2)}%) ({item['shop']} {item['sku']} {item['update_time']})")

        product = existing_products.get((item["shop"], item["sku"]))

        if product is not None:
            if item["update_time"] > product.update_time:
                # Update existing record.
                product.shop = item["shop"]
                product.sku = item["sku"]
                product.brand_name = item["brand_name"]
                product.name = item["name"]
                product.uom = item["uom"]
                product.url = item["url"]
                product.update_time = item["update_time"]
        else:
            # Insert new record.
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
            existing_products[item["shop"], item["sku"]] = product

        # Add new price record if update time does not exist.
        if product is not None and not any(
                i.update_time.replace(microsecond=0) == item["update_time"].replace(microsecond=0) for i in
                product.prices):
            product.prices.append(Price(
                price=item["price"],
                currency=item["currency"],
                update_time=item["update_time"]
            ))

        # Commit frequency to reduce memory load.
        if i % commit_frequency == 0:
            session.add_all(new_products)
            session.commit()

    session.add_all(new_products)
    session.commit()


def clean_item(item):
    item["update_time"] = clean_item_update_time(update_time=item["update_time"])
    item["price"] = clean_item_price(price=item["price"])
    return item


def clean_item_update_time(update_time):
    if update_time is None:
        return None

    if isinstance(update_time, datetime):
        return update_time

    if isinstance(update_time, (int, float)):
        try:
            return datetime.utcfromtimestamp(update_time)
        except (ValueError, OverflowError):
            return datetime.utcfromtimestamp(update_time / 1000)

    if isinstance(update_time, str):
        return datetime.strptime(update_time, "%Y-%m-%d %H:%M:%S")

    raise TypeError(f"unknown type {type(update_time)}.")


def clean_item_price(price):
    if price is None:
        return None

    if isinstance(price, (int, float, str)):
        return float(price)

    raise TypeError(f"unknown type {type(price)}.")


def main(file_count=1, demo=False):
    sftp = get_sftp_session()
    db = get_db_session()

    dirs = ["/home/data/park_n_shop"]
    files = sorted([os.path.join(dir_, f) for dir_ in dirs for f in sftp.listdir(dir_) if f[-5:] == ".json"],
                   reverse=True)
    for file in files[:file_count]:
        with sftp.file(filename=file) as f:
            items = json.load(f)
            logging.info(f"processing {file} {len(items)} items")

            if not demo:
                update_product_price_records(session=db, items=items)

    sftp.close()
    db.close()


if __name__ == "__main__":
    main()
