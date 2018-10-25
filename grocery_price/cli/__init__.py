import click

from grocery_price.cli.crawl import crawl
from grocery_price.cli.download import download
from grocery_price.cli.list import list
from grocery_price.cli.load import load
from grocery_price.cli.start_bot import start_bot


@click.group()
def cli():
    pass


cli.add_command(download)
cli.add_command(load)
cli.add_command(list)
cli.add_command(start_bot)
cli.add_command(crawl)
