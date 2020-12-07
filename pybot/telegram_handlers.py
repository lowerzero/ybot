from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from pybot import bot_instance, set_status, OWNER_ID, set_rate
from pybot.downloader import Downloader


def echo(update, context):
    if update.message.from_user.id != OWNER_ID:
        update.message.reply_text('💩')
        return

    keyboard = [[InlineKeyboardButton("Download", callback_data='Download')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(update.message.text, reply_markup=reply_markup)


def callback(update, context):
    query = update.callback_query

    query.answer()

    if query.data == "Download":
        set_status(query.message.message_id, query.message.chat_id, "Accepted")
        dl = Downloader(query.message.message_id,
                        query.message.chat_id,
                        query.message.text)
        dl.start()

    elif query.data == "Reset":
        set_status(query.message.message_id, query.message.chat_id, "Download", reset_name="blocked")

    elif query.data in ['rate+', 'rate-']:
        set_rate(query.message.message_id, query.message.chat_id, query.data)
