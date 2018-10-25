import traceback
from datetime import datetime
from itertools import groupby

import click

from grocery_price.cli.utils.repository import get_repository_handler
from grocery_price.models import Price, Product, get_session as get_db_session


@click.command()
@click.argument("spider_name")
@click.argument("filename", required=False)
@click.option("--file-count", type=int, required=False, default=10, help="Number of item files to process.")
@click.option("--feed-uri", envvar="FEED_URI", hidden=True)
@click.option("--database-uri", envvar="DATABASE_URI", hidden=True)
def load(feed_uri, database_uri, spider_name, filename, file_count):
    """Load items to database.

    By default, load only the latest 10 item files.
    Already loaded item files will be skipped.
    Data cleaning will be applied to items before loading.
    """
    repo = get_repository_handler(feed_uri=feed_uri)

    x = repo.get_item_files(spider_name=spider_name) if filename is None else [filename]
    filenames = sorted(x, reverse=True)[:file_count]

    db_session = get_db_session(database_uri)
    loaded_filenames = {r.source_filename for r in
                        db_session.query(Price.source_filename).filter(Price.source_filename.in_(filenames)).distinct()}
    db_session.close()

    for i, filename in enumerate(filenames, start=1):

        # Load latest item files first. Skip already loaded item files.
        if filename in loaded_filenames:
            click.echo(f"({i}/{len(filenames)}) {filename}: Skipped loaded file")
            continue

        click.echo(f"({i}/{len(filenames)}) {filename}: Loading items...", nl=False)

        try:
            items = repo.get_items_from_item_file(spider_name=spider_name, filename=filename)
            cleaned_items = get_cleaned_items(items=items, spider_name=spider_name, filename=filename)

            click.echo(f"{len(cleaned_items)} items found...", nl=False)

            click.echo("Uploading...", nl=False)

            db_session = get_db_session(database_uri)
            load_items(
                source_filename=filename,
                items=cleaned_items,
                session=db_session
            )
            db_session.close()

            click.echo("Done")

        except Exception:
            click.echo("Error!!!")
            click.echo(traceback.format_exc())


def get_cleaned_items(items, spider_name, filename):
    cleaned_items = []

    for i in items:

        # Incorrect year in update_time. (e.g. '14-01-16 14:00:21').
        if isinstance(i["update_time"], str) and i["update_time"][2] == "-":
            i["update_time"] = (filename[:4] + i["update_time"][2:])

        cleaned_items.append(i)

    return cleaned_items


def load_items(items, session, source_filename=None):
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
    items = [prepare_item_for_load_to_database(i) for i in items]

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


def prepare_item_for_load_to_database(item):
    item["update_time"] = prepare_update_time(update_time=item.get("update_time"))
    item["price"] = prepare_price(price=item.get("price"))
    item["brand_name"] = prepare_brand_name(brand_name=item.get("brand_name"))
    return item


def prepare_update_time(update_time):
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


def prepare_price(price):
    if price is None:
        return None

    if isinstance(price, (int, float, str)):
        return float(price)

    raise TypeError(f"unknown type {type(price)}.")


def prepare_brand_name(brand_name):
    if brand_name is None:
        return None

    return brand_name
