import logging
import os

from telegram.ext import Updater

from grocery_price.bot.find import find_handler

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logging.getLogger("telegram.ext.dispatcher").setLevel(logging.DEBUG)


def start():
    updater = Updater(os.environ.get("TELEGRAM_TOKEN"))
    dispatcher = updater.dispatcher
    dispatcher.add_handler(find_handler)
    updater.start_polling()
