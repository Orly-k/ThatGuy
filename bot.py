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

bot_manager = {"new_event": 0, "manager": 0, "guest": 0, "open_list": 0, "closed_list": 0, "I_wanna_bring": 0,\
               "bringing": 0, "expenses": 0, "reminder_for_clumsys": 0, "close_list": 0, "set_balance": 0}
group_password = {}
group_manager_password = {}

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

        bot_manager["manager"] = 0
        logger.info(f"chat_id:{chat_id}, text {text}")

        if storage.set_manager(chat_id, text):
            storage.set_user_id(text, chat_id)
            group_manager_password[chat_id] = text
            response = "You are the boss! you can do whatever you want!"

        else:
            response = "You're rude! are you trying to take over?"

        bot.send_message(chat_id=chat_id,
                         text=response)

    elif bot_manager["open_list"]:

        if not bot_manager["closed_list"]:
            bot_manager["open_list" ] = 0
            keyword_add = "add"
            keyword_remove = "remove"

            if text[:len(keyword_add)] == keyword_add:

                response = f"{text[len(keyword_add) + 1:]} has been added" if storage.add_item_to_list(chat_id, text[len(keyword_add) + 1:]) \
                    else f"{text[len(keyword_add) + 1:]} is already in the list"

            elif text[:len(keyword_remove)] == keyword_remove:

                response = f"{text[len(keyword_remove)+ 1:]} has been removed" if storage.remove_item_from_list(chat_id,text[len(keyword_remove) + 1:]) \
                    else f"{text[len(keyword_remove) + 1:]} was not found"

        else:
            response = "want anything else?  organize another party"

        bot.send_message(chat_id=chat_id, text=response)

    elif bot_manager["I_wanna_bring"]:

        bot_manager["I_wanna_bring"] = 0
        bot_manager["bringing"] = 1

        remaining_items = storage.get_remaining_items(text)
        logger.info(f"remaining_items:{text}")
        group_password[chat_id] = text
        response = "Items you can bring:\n"
        response += "\n".join(f"{i+1}. {s}" for i, s in enumerate(remaining_items))
        bot.send_message(chat_id=chat_id, text=response)

    elif bot_manager["bringing"]:
        bot_manager["expenses"] = 1
        bot_manager["bringing"] = 0
        response = "So far so good, How much money are you spending?" if storage.set_taken_item(group_password[chat_id], text)\
            else "Are you bringing weird things?"

        bot.send_message(chat_id=chat_id, text=response)

    elif bot_manager["expenses"]:
        bot_manager["expenses"] = 0
        storage.set_costs(group_password[chat_id], text, chat_id)
        bot.send_message(chat_id=chat_id, text="we'll pick up tabs later")

    elif bot_manager["reminder_for_clumsys"]:

        bot_manager["reminder_for_clumsys"] = 0

        if storage.get_manager_id(text, chat_id):

            clumsys = storage.get_all_clumsys(text)

            for clumsy in clumsys:
                bot.send_message(chat_id=clumsy, text="Why aren’t you bringing anything to the party? so rude! ")
            response = "I told them, they better do something about it"

        else:
            response = "Who do you think you are?! you're not entitled, too bad for you!"

        bot.send_message(chat_id=chat_id, text=response)



    elif bot_manager["close_list"]:

        bot_manager["close_list"] = 0

        if storage.get_manager_id(text, chat_id):
            bot_manager["closed_list"] = 1
            response = "The list has been closed"

        else:
            response = "Who do you think you are?! you're not entitled to close the list!"

        bot.send_message(chat_id=chat_id, text=response)

    elif bot_manager["set_balance"]:

        if storage.get_manager_id(text, chat_id):
            storage.set_balance(text)
            response = "OK than, balanced is set"

        else:
            response = "Who do you think you are?! you're not entitled, too bad for you!"

        bot.send_message(chat_id=chat_id, text=response)

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
    event_password = str(chat_id) + "_" + text
    storage.set_password(chat_id, event_password)
    return event_password

def edit_list(bot, update):

    chat_id = update.message.chat_id

    if not bot_manager["closed_list"]:
        logger.info(f"add to list = Got on chat #{chat_id}")
        bot_manager["open_list"] = 1
        response = "Start adding/removing items to list\nTo add item use keyword \"add\"\nTo remove item use keyword \"remove\""

    else:
        response = "want anything else?  organize another party"
    bot.send_message(chat_id=chat_id,
                     text=response)

def show_list(bot, update):

    chat_id = update.message.chat_id
    logger.info(f"- Show items: chat #{chat_id}")
    items = storage.get_items(chat_id)
    response = "Our event list:\n"
    response += "\n".join(f"{i+1}. {s}" for i, s in enumerate(items))
    bot.send_message(chat_id=update.message.chat_id, text=response)

def I_wanna_bring(bot, update):

    chat_id = update.message.chat_id
    bot_manager["I_wanna_bring"] = 1
    bot.send_message(chat_id=chat_id,text="Enter password")

def reminder_for_clumsys(bot, update):

    bot_manager["reminder_for_clumsys"] = 1
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text="Enter password")

def close_list(bot, update):
    bot_manager["close_list"] = 1
    bot_manager["closed_list"] = 1
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text="Enter password")

def set_balance(bot, update):

    chat_id = update.message.chat_id

    if  bot_manager["closed_list"] == 1:
        bot_manager["set_balance"] = 1
        response = "enter password"

    else:
        response = "What are you trying to do? give people a chance to participate, you weirdo"

    bot.send_message(chat_id=chat_id, text=response)

start_handler = CommandHandler('start', start)
guest_handler = CommandHandler('guest', guest)
new_event_handler = CommandHandler('new_event', new_event)
manager_handler = CommandHandler('set_manager', set_manager)
edit_list_handler = CommandHandler('edit_list', edit_list)
show_handler = CommandHandler('show_list', show_list)
bring_handler = CommandHandler('I_wanna_bring', I_wanna_bring)
clumsys_handler = CommandHandler('reminder_for_clumsys', reminder_for_clumsys)
close_list_handler = CommandHandler('close_list', close_list)
set_balance_handler = CommandHandler('set_balance', set_balance)



dispatcher.add_handler(start_handler)
dispatcher.add_handler(guest_handler)
dispatcher.add_handler(new_event_handler)
dispatcher.add_handler(manager_handler)
dispatcher.add_handler(edit_list_handler)
dispatcher.add_handler(show_handler)
dispatcher.add_handler(bring_handler)
dispatcher.add_handler(clumsys_handler)
dispatcher.add_handler(close_list_handler)
dispatcher.add_handler(set_balance_handler)

echo_handler = MessageHandler(Filters.text, respond)
dispatcher.add_handler(echo_handler)

logger.info("Start polling")

updater.start_polling()
print(secret_settings.BOT_TOKEN)