# {ThatGuy}
{This bot will help you create events!} <https://t.me/{750875810:AAGMTR3EPI8hGjBhEpgJJ8cVLU871QrT7iw}>

* {Orly Kierszenbaum}
* {Hodaya Marciano}

{ThatGuy takes care of who is coming, what needs to be brough to the event, and payment to friends}

## Screenshots

![SCREESHOT DECSRIPTION](screenshots/shopping-list-bot-1.png)

## How to Run This Bot
You can use /help for full instructions.
use /new_event in a groupe chat in order to create a new event. Save the password for further accsses to event.
set an event manager with: /set_manager. The manager will take care of payment and reminders.
if you are invaited to an event type /guest to RSVP
use /show_list to see menu
use /edit_list if you want to add/remove items.
use /I_wanna_bring to tell your friends what you are bringing,update the list so your friends dont bring the same thing and let the manager know how much money you are spending.

the manager can now close the list with /close_list and /set_balance to calculate who ows how much money.

once the list is closed and the manager calculated the expenses you can check your balance with /get_balance, 
and pay your debt with /pay_now

### Prerequisites
* Python 3.7
* pipenv
* MongoDB
* {ADD MORE DEPENDENCIES HERE}

### Setup
* Clone this repo from github
* Install dependencies: `pipenv install`
* Get a BOT ID from the [botfather](https://telegram.me/BotFather).
* Create a `secret_settings.py` file:

        BOT_TOKEN = "750875810:AAGMTR3EPI8hGjBhEpgJJ8cVLU871QrT7iwe"

### Run
To run the bot use:

    pipenv run python bot.py

(Or just `python bot.py` if running in a pipenv shell.)

## Credits and References
* [Telegram Docs](https://core.telegram.org/bots)
* [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
//* [Telegram Docs]()
//* stackoverflow
* udi's tiny-shopping-list(https://github.com/Elevationacademy/tiny-shopping-list-bot-ella/blob/master/bot.py) :)

