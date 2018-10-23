import traceback

import click

from grocery_price.cli.utils import get_cleaned_items, get_repository_handler
from grocery_price.cli.utils.update_product_price_records import update_product_price_records
from grocery_price.models import Price, get_session as get_db_session


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

    db_session = get_db_session(database_uri)
    loaded_filenames = {r.source_filename for r in db_session.query(Price.source_filename).distinct()}
    db_session.close()

    # Load latest item files first. Skip already loaded item files.
    x = repo.get_item_files(spider_name=spider_name) if filename is None else [filename]
    filenames = sorted(x, reverse=True)[:file_count]

    for i, filename in enumerate(filenames, start=1):

        if filename in loaded_filenames:
            click.echo(f"({i}/{len(filenames)}) {filename}: Skipped loaded file")
            continue

        click.echo(f"({i}/{len(filenames)}) {filename}: Loading items...", nl=False)

        try:
            items = repo.get_items_from_item_file(spider_name=spider_name, filename=filename)
            cleaned_items = get_cleaned_items(items=items, spider_name=spider_name, filename=filename)

            click.echo(f"{len(cleaned_items)} items found...", nl=False)

            db_session = get_db_session(database_uri)
            update_product_price_records(
                source_filename=filename,
                items=cleaned_items,
                session=db_session,
                show_progress=True
            )
            db_session.close()

        except Exception:
            click.echo("Error!!!")
            click.echo(traceback.format_exc())
