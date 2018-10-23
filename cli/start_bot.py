import click

from bot import start


@click.command()
def start_bot():
    """Start Telegram bot.
    """
    start()
