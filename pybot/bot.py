from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from pybot import TOKEN
from pybot.telegram_handlers import echo, callback


def start_listener():
    updater = Updater(TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', echo))
    updater.dispatcher.add_handler(CallbackQueryHandler(callback))

    updater.start_polling()

    updater.idle()
