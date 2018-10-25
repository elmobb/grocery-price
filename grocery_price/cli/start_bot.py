import click


@click.command()
def start_bot():
    """Start Telegram bot.
    """
    from grocery_price.bot import start
    start()
