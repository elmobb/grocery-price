import click

from cli.download import download
from cli.list import list
from cli.load import load
from cli.start_bot import start_bot


@click.group()
def cli():
    pass


cli.add_command(download)
cli.add_command(load)
cli.add_command(list)
cli.add_command(start_bot)
