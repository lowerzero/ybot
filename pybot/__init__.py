import os
from queue import Queue

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = os.getenv('TOKEN')
TCD_QUEUE = Queue()
SEND_QUEUE = Queue()
WORKDIR = os.getenv('WORKDIR')

OWNER_ID = os.getenv('OWNER_ID')
PUBLIC_CHANNEL = os.getenv('PUBLIC_CHANNEL')

FILESIZE_LIMIT = 51380224

FFMPEG_THREADS = os.getenv('FFMPEG_THREADS')


def bot_instance():
    return Bot(TOKEN)


def set_rate(message_id, chat_id, rate):
    rates = {
        'rate+': '✨😎✨',
        'rate-': '✨💩✨'
    }

    keyboard = [
        [InlineKeyboardButton(rates[rate], callback_data="blocked")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    bot_instance().edit_message_reply_markup(
        message_id=message_id,
        chat_id=chat_id,
        reply_markup=reply_markup)


def set_status(message_id, chat_id, status, reset_name='Reset'):
    keyboard = [
        [InlineKeyboardButton(status, callback_data=status)],
        [InlineKeyboardButton("Reset", callback_data=reset_name)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    bot_instance().edit_message_reply_markup(
        message_id=message_id,
        chat_id=chat_id,
        reply_markup=reply_markup
    )


def send_photo(chat_id, img):
    keyboard = [
        [InlineKeyboardButton('😎', callback_data='rate+'),
         InlineKeyboardButton('💩', callback_data='rate-')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot_instance().send_photo(chat_id=chat_id,
                              photo=img,
                              reply_markup=reply_markup)


def send_audio(chat_id, audio, title):
    bot_instance().send_audio(chat_id=chat_id,
                              audio=audio,
                              title=title,
                              performer='YT',
                              timeout=660)
