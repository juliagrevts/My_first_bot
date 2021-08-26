import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from ephem import *

import settings

logging.basicConfig(filename='bot.log', level=logging.INFO)

PROXY = {'proxy_url': settings.PROXY_URL,
    'urllib3_proxy_kwargs': {'username': settings.PROXY_USERNAME, 'password': settings.PROXY_PASSWORD}}

planets_dict = {
    'Mars': Mars(),
    'Jupiter': Jupiter(), 
    'Saturn': Saturn(), 
    'Mercury': Mercury(), 
    'Uranus': Uranus(), 
    'Venus': Venus(), 
    'Neptune': Neptune()
}

def greet_user(update, context):
    print('Вызван /start')
    update.message.reply_text('Привет, пользователь!')

def name_constellation(update, context):
    user_input = update.message.text.split()
    if len(user_input) > 2:
        update.message.reply_text('Нужно передать только одну планету')
    else:
        user_planet = user_input.pop().capitalize()
        if user_planet in planets_dict:
            get_planet = planets_dict[user_planet]
            get_planet.compute()
            get_constellation = constellation(get_planet)
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