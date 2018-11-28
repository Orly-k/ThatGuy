from random import randint
from time import sleep
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext import Updater
from functools import wraps
from telegram import ChatAction
import telegram
import logging

import model
import secret_settings
import settings

storage = model.Storage(settings.HOST, settings.DB)

logging.basicConfig(
    format='[%(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

updater = Updater(token=secret_settings.BOT_TOKEN)
dispatcher = updater.dispatcher

def start(bot, update):
    password_keyboard = [['The boss password']]
    menu_markup = ReplyKeyboardMarkup(password_keyboard, one_time_keyboard=True, resize_keyboard=True)
    chat_id = update.message.chat_id
    logger.info(f"> Start chat #{chat_id}")
    bot.send_message(chat_id=chat_id, text="Welcome to ThatGuy bot!\nYou are the boss!\nChoose a password so nobody else can know our secrets.",
                     reply_markup = menu_markup)
#     choose gif

def respond(bot, update):
    chat_id = update.message.chat_id
    text = update.message.text

    logger.info(f"= Got on chat #{chat_id}: {text!r}")

    if text == 'The boss password':
        response = "OK, Enter password.\n"
        bot.send_message(chat_id=update.message.chat_id, text=response)
    else:
        password(chat_id, text)

def password(chat_id, text):

    logger.info(f"password function = Got on chat #{chat_id}: {text!r}")

    if not password.is_password_set:
        logger.info(f"password function first time")

        storage.set_password(chat_id, text)
        password.is_password_set = 1
    else:
        pass
        # send angry gif

password.is_password_set = 0

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

echo_handler = MessageHandler(Filters.text, respond)
dispatcher.add_handler(echo_handler)

logger.info("Start polling")
updater.start_polling()
print(secret_settings.BOT_TOKEN)
