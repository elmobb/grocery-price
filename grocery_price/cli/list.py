import click

from grocery_price.cli.utils.repository import get_repository_handler


@click.command()
@click.argument("spider_name", required=False)
@click.option("--feed-uri", envvar="FEED_URI", hidden=True)
def list(spider_name, feed_uri):
    """List spiders or spider's item files.

    Lists spiders if SPIDER_NAME is not provided. Otherwise, list all item files of SPIDER_NAME.
    """
    repo = get_repository_handler(feed_uri=feed_uri)

    if spider_name is None:
        # List spiders.
        for i in sorted(repo.get_spider_names()):
            click.echo(i)

    else:
        # List spider files.
        files = repo.get_item_files(spider_name=spider_name)
        click.echo(f"Found {len(files)} files.")
        for i in sorted(files, reverse=True):
            click.echo(i)

    repo.close()
