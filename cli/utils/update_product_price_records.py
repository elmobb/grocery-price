from datetime import datetime

import click

from models import Price, Product


def update_product_price_records(items, session, commit_frequency=1000, show_progress=False, source_filename=None):
    """Upload Scrapy price items to database.

    Only the latest product details will be kept. All price records will be kept.
    Uploading same set of items in 1 or multiple batches should have the same result.
    """
    existing_products = {(i.shop, i.sku): i for i in session.query(Product).filter_by().all()}
    new_products = []

    if show_progress:
        click.echo("Uploading...")

    # Ensure the latest version of product is updated first.
    with click.progressbar(sorted(items, key=lambda i: i["update_time"], reverse=True)) as bar:
        for i, item in enumerate(bar, start=1):

            item = clean_item(item=item)

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
                    if source_filename is not None:
                        product.source_filename = source_filename
            else:
                # Insert new record.
                product = Product(
                    shop=item["shop"],
                    sku=item["sku"],
                    brand_name=item["brand_name"],
                    name=item["name"],
                    uom=item["uom"],
                    url=item["url"],
                    update_time=item["update_time"],
                    source_filename=source_filename
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
                    update_time=item["update_time"],
                    source_filename=source_filename
                ))

            # Commit frequency to reduce memory load.
            if i % commit_frequency == 0:
                session.add_all(new_products)
                session.commit()
                new_products = []

    # Ensure all items are uploaded.
    session.add_all(new_products)
    session.commit()


def clean_item(item):
    item["update_time"] = clean_item_update_time(update_time=item.get("update_time"))
    item["price"] = clean_item_price(price=item.get("price"))
    item["brand_name"] = clean_item_brand_name(brand_name=item.get("brand_name"))
    return item


def clean_item_update_time(update_time):
    if update_time is None:
        return None

    if isinstance(update_time, datetime):
        return update_time

    if isinstance(update_time, (int, float)):
        try:
            return datetime.utcfromtimestamp(update_time)
        except (ValueError, OverflowError, OSError):
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


def clean_item_brand_name(brand_name):
    if brand_name is None:
        return None

    return brand_name
