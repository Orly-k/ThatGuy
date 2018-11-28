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

bot_manager = {"new_event": 0,"manager": 0, "guest": 0}

logging.basicConfig(
    format='[%(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

updater = Updater(token=secret_settings.BOT_TOKEN)
dispatcher = updater.dispatcher

def start(bot, update):
    chat_id = update.message.chat_id
    logger.info(f"> Start chat #{chat_id}")
    bot.send_message(chat_id=chat_id, text="Welcome to ThatGuy bot!\n")
#    only 2 options

def respond(bot, update):

    chat_id = update.message.chat_id
    text = update.message.text

    logger.info(f"= Got on chat #{chat_id}: {text!r}")

    if bot_manager["new_event"]:

        event_pass = password(chat_id, text)
        bot.send_message(chat_id=chat_id,
                         text=f"The password for the party is: {event_pass}")
        bot_manager["new_event"] = 0

    elif bot_manager["guest"]:

        event_password = text
        storage.set_user_id(event_password, chat_id)
        bot_manager["guest"] = 0
        bot.send_message(chat_id=chat_id,
                         text="Bring good things, OK?")


    elif bot_manager["manager"]:

        # check if the manager has been set
        bot_manager["manager"] = 0
        storage.set_manager(chat_id, text)
        bot.send_message(chat_id=chat_id,
                         text="You are the boss! you can do whatever you want!")


    # response = "OK, Your password is set.\n\nEnter your event wish list:"
    # bot.send_message(chat_id=update.message.chat_id, text=response)

def new_event(bot, update):

    bot_manager["new_event"] = 1
    chat_id = update.message.chat_id
    logger.info(f"> new_event chat #{chat_id}")

    bot.send_message(chat_id=chat_id,
                     text="All right than\nChoose your event name to avoid unwelcommed friends")

def set_manager(bot, update):

    bot_manager["manager"] = 1
    chat_id = update.message.chat_id
    logger.info(f">set_manager chat #{chat_id}")

    bot.send_message(chat_id=chat_id,
                     text="All right than\nWhat is your event password?")


def guest(bot, update):

    bot_manager["guest"] = 1
    chat_id = update.message.chat_id

    logger.info(f"> guest chat #{chat_id}")
    bot.send_message(chat_id=chat_id,
                     text="What is your event password?")


def password(chat_id, text):

    logger.info(f"password function = Got on chat #{chat_id}: {text!r}")
    event_password = str(chat_id) + "_"+ text
    storage.set_password(chat_id, event_password)
    return event_password



start_handler = CommandHandler('start', start)
guest_handler = CommandHandler('guest', guest)
new_event_handler = CommandHandler('new_event', new_event)
manager_handler = CommandHandler('set_manager', set_manager)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(guest_handler)
dispatcher.add_handler(new_event_handler)
dispatcher.add_handler(manager_handler)

echo_handler = MessageHandler(Filters.text, respond)
dispatcher.add_handler(echo_handler)

logger.info("Start polling")
updater.start_polling()
print(secret_settings.BOT_TOKEN)
