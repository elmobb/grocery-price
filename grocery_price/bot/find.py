from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackQueryHandler, CommandHandler, ConversationHandler

from grocery_price.bot.utils import find_minimum_price, find_products, get_filter_keys

KEYWORDS, BRAND_NAME, PRODUCT_NAME, UOM, SHOP, ACTION = range(6)


def find_products_by_chat_data(chat_data):
    return find_products(
        keywords=chat_data.get("keywords"),
        shop=chat_data.get("shop"),
        brand_name=chat_data.get("brand_name"),
        name=chat_data.get("name"),
        uom=chat_data.get("uom")
    )


def start(bot, update, chat_data, args):
    chat_data.clear()  # Prevent this find being affected by previous chats.
    chat_data["keywords"] = args
    products = find_products_by_chat_data(chat_data=chat_data)

    # No products found.
    if len(products) == 0:
        update.message.reply_text(text="Oops! No products found.")
        return ConversationHandler.END

    # Send welcome message.
    update.message.reply_text(
        "Hi! Are you looking for a product?\nSend /cancel to cancel.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{i[0]} ({i[1]})", callback_data=i[0])] for i in get_filter_keys(
                products=products,
                key="brand_name"
            )
        ])
    )

    return BRAND_NAME


def filter(by):
    """Get filter state function. Filter state filters out products that fulfill criteria.
    """
    states = [BRAND_NAME, PRODUCT_NAME, UOM, SHOP]
    keys = ["brand_name", "name", "uom", "shop"]
    step = [i for i, v in enumerate(keys) if v == by][0]
    has_next_state = (step + 1 < len(states))

    def func(bot, update, chat_data):
        if not has_next_state:
            return select_action(bot=bot, update=update, chat_data=chat_data)

        query = update.callback_query
        chat_data[keys[step]] = query.data
        products = find_products_by_chat_data(chat_data=chat_data)

        # Show product filter key buttons.
        bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
        bot.send_message(
            chat_id=query.message.chat_id,
            text=query.message.text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"{i[0]} ({i[1]})", callback_data=i[0])] for i in get_filter_keys(
                    products=products,
                    key=keys[step + 1]
                )
            ])
        )

        return states[step + 1]

    return func


def select_action(bot, update, chat_data):
    query = update.callback_query
    chat_data["product"] = find_products_by_chat_data(chat_data=chat_data)[0]

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
    min_prices = find_minimum_price(
        shop=chat_data['product'].shop,
        sku=chat_data['product'].sku,
        days=[1, 7, 2 * 7, 13 * 7, 52 * 7]
    )
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
        CommandHandler("find", start, pass_chat_data=True, pass_args=True)
    ],
    states={
        # Select a product.
        BRAND_NAME:   [
            CallbackQueryHandler(filter(by="brand_name"), pass_chat_data=True),
            CommandHandler("cancel", cancel)
        ],
        PRODUCT_NAME: [
            CallbackQueryHandler(filter(by="name"), pass_chat_data=True),
            CommandHandler("cancel", cancel)
        ],
        UOM:          [
            CallbackQueryHandler(filter(by="uom"), pass_chat_data=True),
            CommandHandler("cancel", cancel)
        ],
        SHOP:         [
            CallbackQueryHandler(filter(by="shop"), pass_chat_data=True),
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
