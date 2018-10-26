from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackQueryHandler, CommandHandler, ConversationHandler

from grocery_price.bot.utils import find_minimum_price, find_products

KEYWORDS, BRAND_NAME, PRODUCT_NAME, UOM, ACTION = range(5)


def find(bot, update, chat_data, args):
    chat_data["keywords"] = args
    chat_data["products"] = find_products(keywords=chat_data["keywords"])

    # No products found.
    if len(chat_data["products"]) == 0:
        update.message.reply_text(text="Oops! No products found.")
        return ConversationHandler.END

    # Get unique brand names.
    brand_names = list(set(i.brand_name for i in chat_data["products"] if i.brand_name != ""))

    # Send welcome message.
    update.message.reply_text(
        "Hi! Are you looking for a product?\nSend /cancel to cancel.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(i, callback_data=i)] for i in brand_names])
    )

    return BRAND_NAME


def get_filter(step):
    """Get filter state function. Filter state filters out products that fulfill criteria.
    """
    state = [BRAND_NAME, PRODUCT_NAME, UOM]
    keys = ["brand_name", "name", "uom"]
    has_next_state = (step + 1 < len(state))

    def filter_(bot, update, chat_data):
        query = update.callback_query

        chat_data[keys[step]] = query.data

        # Get products fulfilled selection in previous state.
        chat_data["products"] = find_products(
            keywords=chat_data.get("keywords"),
            shop=chat_data.get("shop"),
            brand_name=chat_data.get("brand_name"),
            name=chat_data.get("name"),
            uom=chat_data.get("uom")
        )

        if has_next_state:

            # Get filter keys.
            next_key = keys[step + 1]
            values = list(set(getattr(i, next_key) for i in chat_data["products"] if getattr(i, next_key) != ""))

            # Show product filter key buttons.
            bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
            bot.send_message(
                chat_id=query.message.chat_id,
                text=query.message.text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(i, callback_data=i)] for i in values])
            )

            return state[step + 1]

        chat_data["product"] = chat_data["products"][0]

        # Show action buttons.
        bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
        bot.send_message(
            chat_id=query.message.chat_id,
            text=f"What do you want to know about *{chat_data['product'].name} ({chat_data['product'].uom})* in *{chat_data['product'].shop}* (sku: {chat_data['product'].sku})?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("View", callback_data="view", url=chat_data["product"].url)],
                [InlineKeyboardButton("Low", callback_data="low")]
            ])
        )

        return ACTION

    return filter_


def action(bot, update, chat_data):
    query = update.callback_query

    if query.data == "view":
        return ConversationHandler.END

    if query.data == "low":
        return low(bot=bot, update=update, chat_data=chat_data)

    raise NotImplementedError


def low(bot, update, chat_data):
    query = update.callback_query

    # Show low price text message.
    min_prices = find_minimum_price(shop=chat_data['product'].shop, sku=chat_data['product'].sku,
                                    days=[1, 7, 2 * 7, 13 * 7, 52 * 7])
    bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
    bot.send_message(
        chat_id=query.message.chat_id,
        text="\n".join([
            f"Here are the lowest prices of *{chat_data['product'].name} ({chat_data['product'].uom})* in *{chat_data['product'].shop}* (sku: {chat_data['product'].sku}):",
            "",
            f"Today lowest: {min_prices[1]}",
            f"1-Week lowest: {min_prices[7]}",
            f"2-Week lowest: {min_prices[14]}",
            f"13-Week lowest: {min_prices[91]}",
            f"52-Week lowest: {min_prices[364]}"
        ]),
        parse_mode="Markdown"
    )

    return ConversationHandler.END


def cancel(bot, update):
    # Send goodbye message.
    update.message.reply_text(
        text="Bye! I hope we can talk again some day.",
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


find_handler = ConversationHandler(
    entry_points=[
        CommandHandler("find", find, pass_chat_data=True, pass_args=True)
    ],
    states={
        # Select a product.
        BRAND_NAME:   [
            CallbackQueryHandler(get_filter(step=0), pass_chat_data=True),
            CommandHandler("cancel", cancel)
        ],
        PRODUCT_NAME: [
            CallbackQueryHandler(get_filter(step=1), pass_chat_data=True),
            CommandHandler("cancel", cancel)
        ],
        UOM:          [
            CallbackQueryHandler(get_filter(step=2), pass_chat_data=True),
            CommandHandler("cancel", cancel)
        ],
        # Choose action.
        ACTION:       [
            CallbackQueryHandler(action, pass_chat_data=True),
            CommandHandler("cancel", cancel)
        ]
    },
    fallbacks=[
        CommandHandler("cancel", cancel)
    ]
)
