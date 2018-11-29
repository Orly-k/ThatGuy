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


def send_action(action):
    """Sends `action` while processing func command."""
    def decorator(func):
        @wraps(func)
        def command_func(*args, **kwargs):
            bot, update = args
            bot.send_chat_action(chat_id=update.message.chat_id, action=action)
            func(bot, update, **kwargs)

        return command_func

    return decorator

@send_action(ChatAction.TYPING)
def typing(bot, update):
    sleep(2)

def send_gif(bot,image_url, chat_id):

    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
    bot.sendDocument(chat_id=chat_id, document=image_url)

storage = model.Storage(settings.HOST, settings.DB)

bot_manager = {"new_event": 0, "manager": 0, "guest": 0, "open_list": 0, "closed_list": 0, "I_wanna_bring": 0,\
               "bringing": 0, "expenses": 0, "reminder_for_clumsys": 0, "close_list": 0, "set_balance": 0, "is_balance": 0,\
               "get_balance": 0, "pay": 0, "reminder_for_cheaps": 0}

group_password = {}
group_manager_password = {}

logging.basicConfig(
    format='[%(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)
updater = Updater(token=secret_settings.BOT_TOKEN)
dispatcher = updater.dispatcher

def start(bot, update):

    typing(bot, update)
    chat_id = update.message.chat_id
    logger.info(f"> Start chat #{chat_id}")
    bot.send_message(chat_id=chat_id, text="Welcome to ThatGuy bot!")
    send_gif(bot, "https://tenor.com/view/stewie-family-guy-happy-gif-12055489", chat_id)
    typing(bot, update)
    bot.send_message(chat_id=chat_id, text="\n\nfor a new event press:  /new_event\nfor join as guet please press:  /guest\nfor set menejer pres:  /manager")


def respond(bot, update):

    chat_id = update.message.chat_id
    text = update.message.text
    logger.info(f"= Got on chat #{chat_id}: {text!r}")

    keyword_add = "add"
    keyword_remove = "remove"

    if bot_manager["new_event"]:

        typing(bot, update)
        event_pass = password(chat_id, text)
        bot.send_message(chat_id=chat_id,
                         text=f"The password for the party is: {event_pass}")
        bot_manager["new_event"] = 0

    elif bot_manager["guest"]:

        typing(bot, update)
        event_password = text
        storage.set_user_id(event_password, chat_id)
        bot_manager["guest"] = 0
        bot.send_message(chat_id=chat_id,
                         text="Bring good things, OK?")

    elif bot_manager["manager"]:

        typing(bot, update)
        bot_manager["manager"] = 0
        logger.info(f"chat_id:{chat_id}, text {text}")

        if storage.set_manager(chat_id, text):

            storage.set_user_id(text, chat_id)
            group_manager_password[chat_id] = text
            send_gif(bot, "https://tenor.com/view/family-guy-stewie-workout-dance-gif-9584153", chat_id)
            response = "You are the boss! you can do whatever you want!"

        else:
            send_gif(bot, "https://tenor.com/view/family-guy-stewie-griffin-mad-angry-annoyed-gif-7878435", chat_id)
            response = "You're rude! are you trying to take over?"

        bot.send_message(chat_id=chat_id,
                         text=response)

    elif text[:len(keyword_add)] == keyword_add or text[:len(keyword_remove)] == keyword_remove:

        typing(bot, update)
        response = ""

        if not bot_manager["closed_list"]:
            bot_manager["open_list" ] = 0

            if text[:len(keyword_add)] == keyword_add:

                response = f"{text[len(keyword_add) + 1:]} has been added\nThe party is growing!!" if storage.add_item_to_list(chat_id, text[len(keyword_add) + 1:]) \
                    else f"{text[len(keyword_add) + 1:]} is already in the list\nRead the list before approach me!"

            elif text[:len(keyword_remove)] == keyword_remove:

                response = f"{text[len(keyword_remove)+ 1:]} has been removed\nAre you sure? it's a big party,\ntoo bad!" if storage.remove_item_from_list(chat_id,text[len(keyword_remove) + 1:]) \
                    else f"{text[len(keyword_remove) + 1:]} was not found\nRead the list before approaching me!"

        else:
            response = "want anything else?"
            bot.send_message(chat_id=chat_id, text=response)
            typing(bot, update)
            response = "organize another party"

        bot.send_message(chat_id=chat_id, text=response)

    elif bot_manager["I_wanna_bring"]:

        typing(bot, update)
        bot_manager["I_wanna_bring"] = 0
        bot_manager["bringing"] = 1

        remaining_items = storage.get_remaining_items(text)
        logger.info(f"remaining_items:{text}")
        group_password[chat_id] = text
        response = "Items you can bring:\n\n"
        response += "\n".join(f"{i+1}. {s}" for i, s in enumerate(remaining_items))
        bot.send_message(chat_id=chat_id, text=response)

    elif bot_manager["bringing"]:

        typing(bot, update)
        bot_manager["expenses"] = 1
        bot_manager["bringing"] = 0
        response = "So far so good, How much money are you spending?" if storage.set_taken_item(group_password[chat_id], text)\
            else "Are you bringing weird things?"

        bot.send_message(chat_id=chat_id, text=response)

    elif bot_manager["expenses"]:

        typing(bot, update)

        bot_manager["expenses"] = 0
        storage.set_costs(group_password[chat_id], text, chat_id)
        bot.send_message(chat_id=chat_id, text="we'll pick up tabs later")

    elif bot_manager["reminder_for_clumsys"]:

        typing(bot, update)

        bot_manager["reminder_for_clumsys"] = 0

        if storage.get_manager_id(text, chat_id):

            clumsys = storage.get_all_clumsys(text)

            for clumsy in clumsys:
                bot.send_message(chat_id=clumsy, text="Why aren’t you bringing anything to the party? so rude! ")
                send_gif(bot, "https://tenor.com/view/family-guy-stewie-griffin-mad-angry-annoyed-gif-7878435", clumsy)

            response = "I told them, they better do something about it"
            send_gif(bot, "https://tenor.com/view/stewie-griffin-family-guy-stewie-family-guy-drunk-laughing-gif-12774171", chat_id)

        else:
            response = "Who do you think you are?! you're not entitled, too bad for you!"

        bot.send_message(chat_id=chat_id, text=response)

    elif bot_manager["close_list"]:

        typing(bot, update)

        bot_manager["close_list"] = 0

        if storage.get_manager_id(text, chat_id):
            bot_manager["closed_list"] = 1
            response = "The list has been closed, Be happy with what you have"

        else:
            response = "Who do you think you are?! you're not entitled to close the list!"

        bot.send_message(chat_id=chat_id, text=response)

    elif bot_manager["set_balance"]:

        typing(bot, update)

        bot_manager["set_balance"] = 0
        if storage.get_manager_id(text, chat_id):
            storage.set_balance(text)
            response = "OK than, balanced is set"

        else:
            response = "Who do you think you are?! you're not entitled, too bad for you!"

        bot.send_message(chat_id=chat_id, text=response)

    elif bot_manager["get_balance"]:

        typing(bot, update)

        bot_manager["get_balance"] = 0
        response = storage.get_balance(text, chat_id)
        bot.send_message(chat_id=chat_id, text=response)

    elif bot_manager["pay"]:

        typing(bot, update)

        bot_manager["pay"] = 0
        storage.set_who_paid(text, chat_id)
        bot.send_message(chat_id=chat_id, text="Wow! so responsible! are you an adult?")

    elif bot_manager["reminder_for_cheaps"]:

        typing(bot, update)

        bot_manager["reminder_for_cheaps"] = 0
        if storage.get_manager_id(text, chat_id):

            cheaps = storage.get_cheaps(text)
            for cheap in cheaps:
                bot.send_message(chat_id=cheap, text="Why aren’t you paying for the party? so rude! ")
                send_gif(bot, "https://tenor.com/view/money-stewie-familyguy-gif-6188984", cheap)

            send_gif(bot, "https://tenor.com/view/stewie-family-familyguy-cereal-gif-12341914", cheap)
            response = "I told them, they better do something about it"

        else:
            send_gif(bot,
                     "https://tenor.com/view/stewie-family-guy-trippy-gif-4651267", chat_id)
            response = "Who do you think you are?! you're not entitled, too bad for you!"

        bot.send_message(chat_id=chat_id, text=response)


def new_event(bot, update):

    typing(bot, update)

    bot_manager["new_event"] = 1
    chat_id = update.message.chat_id
    logger.info(f"> new_event chat #{chat_id}")
    bot.send_message(chat_id=chat_id,
                     text="All right than\nChoose your event name to avoid unwelcomed friends")
    send_gif(bot,
             "https://tenor.com/view/family-guy-stewie-childhood-gif-3529800", chat_id)


def set_manager(bot, update):

    typing(bot, update)

    bot_manager["manager"] = 1
    chat_id = update.message.chat_id
    logger.info(f">set_manager chat #{chat_id}")
    bot.send_message(chat_id=chat_id,
                     text="All right than\nWhat is your event password?")
def guest(bot, update):

    typing(bot, update)

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

    typing(bot, update)
    chat_id = update.message.chat_id

    if not bot_manager["closed_list"]:
        logger.info(f"add to list = Got on chat #{chat_id}")
        bot_manager["open_list"] = 1
        response = "Start adding/removing items to list\nTo add item use keyword \"add\"\nTo remove item use keyword \"remove\""

    else:
        send_gif(bot, "https://tenor.com/view/stewie-and-brian-brian-and-stewie-stewie-griffin-family-guy-eyes-open-nap-gif-12774067",
                 chat_id)

        response = "want anything else? organize another party"
    bot.send_message(chat_id=chat_id,
                     text=response)

def show_list(bot, update):

    typing(bot, update)
    chat_id = update.message.chat_id
    logger.info(f"- Show items: chat #{chat_id}")
    items = storage.get_items(chat_id)
    response = "Our event list:\n\n"
    response += "\n".join(f"{i+1}. {s}" for i, s in enumerate(items))
    bot.send_message(chat_id=update.message.chat_id, text=response)

def I_wanna_bring(bot, update):

    typing(bot, update)
    chat_id = update.message.chat_id
    bot_manager["I_wanna_bring"] = 1

    bot.send_message(chat_id=chat_id,text="Do you wanna bring things? cool!")
    typing(bot, update)
    bot.send_message(chat_id=chat_id,text="just enter your magic password")

def reminder_for_clumsys(bot, update):

    typing(bot, update)
    bot_manager["reminder_for_clumsys"] = 1
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text="Seriously?! You really need to remind them? What kind of friends are they?\nOK, give me your code")
    send_gif(bot, "https://tenor.com/view/stewie-family-familyguy-cereal-gif-12341914", chat_id)


def close_list(bot, update):

    typing(bot, update)

    bot_manager["close_list"] = 1
    bot_manager["closed_list"] = 1
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text="OK, We'll close the list enter your private number")

def set_balance(bot, update):

    typing(bot, update)


    chat_id = update.message.chat_id

    if  bot_manager["closed_list"] == 1:
        bot_manager["is_balance"] = 1
        bot_manager["set_balance"] = 1
        response = "Do you wanna set the balance list?\nOK than, give me your group magic key'\nand i'll check if you're allowd to do that"

    else:
        typing(bot, update)
        response = "What are you trying to do? give people a chance to participate, you weirdo"
        send_gif(bot, "https://tenor.com/view/family-guy-gif-6229437", chat_id)

    bot.send_message(chat_id=chat_id, text=response)


def get_balance(bot, update):

    typing(bot, update)

    chat_id = update.message.chat_id
    if bot_manager["is_balance"]:
        bot_manager["get_balance"] = 1
        response = "dont just stare! do somthing about it,\nnow, give your private number"
        send_gif(bot, "https://tenor.com/view/stewie-whyyou-murdereyes-gif-5757385", chat_id)
    else:
        response = "You are fast, but your friends are clumsy,\ngo inspire them! "

    bot.send_message(chat_id=chat_id, text=response)

def pay_now(bot, update):

    typing(bot, update)

    chat_id = update.message.chat_id
    bot_manager["pay"] = 1
    bot.send_message(chat_id=chat_id, text="Paying is good!")
    send_gif(bot, "https://tenor.com/view/family-guy-stewie-happy-excited-ecstatic-gif-4427450", chat_id)
    bot.send_message(chat_id=chat_id, text="\njust enter your identifier")


def reminder_for_cheaps(bot, update):

    typing(bot, update)

    bot_manager["reminder_for_cheaps"] = 1
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text="Stingy people are the worst!")
    send_gif(bot, "https://tenor.com/view/breakdance-groovy-jamming-stewie-family-guy-gif-8705114", chat_id)
    bot.send_message(chat_id=chat_id, text="give me your access number and i'll handle it for you!")

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
get_balance_handler = CommandHandler('get_balance', get_balance)
pay_now_handler = CommandHandler('pay_now', pay_now)
reminder_for_cheaps_handler = CommandHandler('reminder_for_cheaps', reminder_for_cheaps)

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
dispatcher.add_handler(get_balance_handler)
dispatcher.add_handler(pay_now_handler)
dispatcher.add_handler(reminder_for_cheaps_handler)

echo_handler = MessageHandler(Filters.text, respond)
dispatcher.add_handler(echo_handler)

logger.info("Start polling")

updater.start_polling()
print(secret_settings.BOT_TOKEN)