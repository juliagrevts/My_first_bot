import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from ephem import *

import settings

logging.basicConfig(filename='bot.log', level=logging.INFO)

PROXY = {'proxy_url': settings.PROXY_URL,
    'urllib3_proxy_kwargs': {'username': settings.PROXY_USERNAME, 'password': settings.PROXY_PASSWORD}}

def greet_user(update, context):
    print('Вызван /start')
    update.message.reply_text('Привет, пользователь!')

def name_constellation(update, context):
    user_planet = update.message.text.split()
    if len(user_planet) > 2:
        update.message.reply_text('Нужно передать только одну планету')
    else:
        get_planet = user_planet.pop().capitalize()
        planets_list = [
            Mars(), 
            Jupiter(), 
            Saturn(), 
            Mercury(), 
            Uranus(), 
            Venus(), 
            Neptune()
        ]
        for planet in planets_list:
            if get_planet == planet.name:
                planet.compute()
                get_constellation = constellation(planet)
                update.message.reply_text(f'Планета сейчас находится в созвездии {get_constellation}')
          
def talk_to_me(update, context):
    text = update.message.text
    print(text)
    update.message.reply_text(text)

def main():
    mybot = Updater(settings.API_KEY, use_context=True, request_kwargs=PROXY)

    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(CommandHandler('planet', name_constellation))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))

    logging.info('Бот стартовал')
    mybot.start_polling()
    mybot.idle()

if __name__ == "__main__":
    main()