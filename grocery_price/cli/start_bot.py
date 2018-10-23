import click

from grocery_price.bot import start


@click.command()
def start_bot():
    """Start Telegram bot.
    """
    start()
