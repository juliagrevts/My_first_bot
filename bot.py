import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import ephem

import settings
import config

logging.basicConfig(filename='bot.log', level=logging.INFO)

PROXY = {'proxy_url': settings.PROXY_URL,
         'urllib3_proxy_kwargs': {'username': settings.PROXY_USERNAME, 'password': settings.PROXY_PASSWORD}}


CITIES_DICT = {}


def greet_user(update, context):
    print('Вызван /start')
    update.message.reply_text('Привет, пользователь!')


def name_constellation(update, context):
    user_input = update.message.text.split()
    if len(user_input) > 2:
        update.message.reply_text('Нужно передать только одну планету')
    else:
        user_planet = user_input.pop().capitalize()
        try:
            planet_name = getattr(ephem, user_planet)
            planet = planet_name()
            planet.compute()
            constellation = ephem.constellation(planet)
            update.message.reply_text(f'Планета сейчас находится в созвездии {constellation}')
        except AttributeError:
            update.message.reply_text('Бот не знает такую планету')


def count_words(update, context):
    user_input = update.message.text.split()
    len_user_input = len(user_input) - 1
    update.message.reply_text(f'{len_user_input} слов')


def determine_full_moon(update, context):
    user_input = update.message.text.split()
    user_date_string = user_input.pop()
    update.message.reply_text(f'Ближайшее полнолуние {ephem.next_full_moon(user_date_string)}')


def play_cities(update, context):
    user_input = update.message.text.split()
    del user_input[0]
    user_city = ' '.join(user_input)
    id = update['message']['chat']['id']
    if id not in CITIES_DICT:
        CITIES_DICT[id] = config.CITIES_LIST
    if user_city in CITIES_DICT[id]:
        CITIES_DICT[id].remove(user_city)
        found_city = False
        for city in CITIES_DICT[id]:
            if user_city[-1].capitalize() == city[0]:
                update.message.reply_text(f'{city}, ваш ход')
                CITIES_DICT[id].remove(city)
                found_city = True
                break
            elif user_city[-1] == 'ь' or 'ы':
                if user_city[-2].capitalize() == city[0]:
                    update.message.reply_text(f'{city}, ваш ход')
                    CITIES_DICT[id].remove(city)
                    found_city = True
                    break
        if not found_city:
            update.message.reply_text(f'Не знаю городов на "{user_city[-1]}", вы выиграли!')
    else:
        update.message.reply_text('В списке у бота нет такого города')


def calculate(update, context):
    user_input = update.message.text.split('/calc')
    user_input = user_input[1].lower().replace(' ', '')
    if len(user_input) < 3:
        update.message.reply_text('Нужно передать минимум 2 числа и знак действия')
        return
    try:
        parts = user_input.split('+')
        for index in range(len(parts)):
            if '-' in parts[index]:
                parts[index] = parts[index].split('-')
        for index in range(len(parts)):
            parts[index] = precalculate(parts[index])
        result = sum(parts)
    except ValueError:
        result = 'Видимо, Вы что-то не то передали'
    except ZeroDivisionError:
        result = 'Нельзя делить на ноль!'
    update.message.reply_text(result)


def precalculate(part):
    if type(part) is str:
        if '*' in part:
            result = 1
            for subpart in part.split('*'):
                result *= precalculate(subpart)
            return result
        elif '/' in part:
            parts = list(map(precalculate, part.split('/')))
            result = parts[0]
            for subpart in parts[1:]:
                result /= subpart
            return result
        else:
            return float(part)
    elif type(part) is list:
        for i in range(len(part)):
            part[i] = precalculate(part[i])
        return part[0]-sum(part[1:])


def talk_to_me(update, context):
    text = update.message.text
    print(text)
    update.message.reply_text(text)


def main():
    mybot = Updater(settings.API_KEY, use_context=True, request_kwargs=PROXY)

    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(CommandHandler('planet', name_constellation))
    dp.add_handler(CommandHandler('wordcount', count_words))
    dp.add_handler(CommandHandler('next_full_moon', determine_full_moon))
    dp.add_handler(CommandHandler('cities', play_cities))
    dp.add_handler(CommandHandler('calc', calculate))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))

    logging.info('Бот стартовал')
    mybot.start_polling()
    mybot.idle()


if __name__ == "__main__":
    main()
