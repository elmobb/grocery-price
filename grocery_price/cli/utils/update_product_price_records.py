from datetime import datetime
from itertools import groupby

from grocery_price.models import Price, Product


def update_product_price_records(items, session, source_filename=None):
    """Upload Scrapy price items to database.

    Only the latest product details will be kept. All price records will be kept.
    Uploading same set of items in 1 or multiple batches should have the same result.
    """
    # Cannot have multiple shops.
    shops = list(set(i["shop"] for i in items))
    assert len(shops) == 1, "cannot update items of multiple shops at a time"
    shop = shops[0]

    # Remove duplicated items by keeping only the latest one.
    groups = groupby(sorted(items, key=lambda i: i["sku"]), key=lambda i: i["sku"])
    items = [sorted(g, key=lambda i: i["update_time"], reverse=True)[0] for sku, g in groups]

    # Cannot have duplicated items.
    skus = [i["sku"] for i in items]
    assert len(skus) == len(set(skus)), f"cannot update same items at a time"

    # Prepare loading to database by converting items' field values to proper formats.
    items = [clean_item(i) for i in items]

    # Get existing products.
    products = {i.sku: i for i in session.query(Product).filter_by(shop=shop).all()}

    # Insert products.
    session.bulk_insert_mappings(Product, [
        {
            "shop":            i["shop"],
            "sku":             i["sku"],
            "brand_name":      i["brand_name"],
            "name":            i["name"],
            "uom":             i["uom"],
            "url":             i["url"],
            "update_time":     i["update_time"],
            "source_filename": source_filename
        } for i in items if i["sku"] not in products
    ])

    # Update products.
    session.bulk_update_mappings(Product, [
        {
            "id":              products[i["sku"]].id,
            "shop":            i["shop"],
            "sku":             i["sku"],
            "brand_name":      i["brand_name"],
            "name":            i["name"],
            "uom":             i["uom"],
            "url":             i["url"],
            "update_time":     i["update_time"],
            "source_filename": source_filename
        } for i in items if i["sku"] in products and i["update_time"] > products[i["sku"]].update_time
    ])

    # Get existing products again since products have been updated.
    products = {i.sku: i for i in session.query(Product).filter_by(shop=shop).all()}

    # Get existing prices.
    update_times = {i["update_time"] for i in items}
    x = session.query(Price).filter(Price.update_time.between(min(update_times), max(update_times))).all()
    prices = {(i.product.sku, i.update_time): i for i in x}

    # Insert prices.
    session.bulk_insert_mappings(Price, [
        {
            "product_id":      products[i["sku"]].id,
            "price":           i["price"],
            "currency":        i["currency"],
            "update_time":     i["update_time"],
            "source_filename": source_filename
        } for i in items if (i["sku"], i["update_time"]) not in prices
    ])

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
