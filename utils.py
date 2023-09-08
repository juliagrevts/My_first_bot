from random import choice, randint

from emoji import emojize
from telegram import KeyboardButton, ReplyKeyboardMarkup

import config


def main_keyboard():
    send_location = KeyboardButton('Мои координаты', request_location=True)
    return ReplyKeyboardMarkup([['Пришли слоника', send_location]])


def set_cities_set(context):
    context.user_data['bot_cities'] = config.CITIES_SET
    context.user_data['user_cities'] = set()


def get_smile(user_data):
    # context.user_data - dict for the user data while the bot is running
    if 'emoji' not in user_data:
        smile = choice(config.EMOJI_LIST)
        user_data['emoji'] = emojize(smile, language='alias')
    return user_data['emoji']


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
        return part[0] - sum(part[1:])


def play_random_numbers(user_int):
    bot_int = randint(user_int - 10, user_int + 10)
    if user_int > bot_int:
        message = f'Ты загадал {user_int}, я загадал {bot_int}, ты выиграл!'
    elif user_int == bot_int:
        message = f'Ты загадал {user_int}, я загадал {bot_int}, ничья!'
    else:
        message = f'Ты загадал {user_int}, я загадал {bot_int}, я выиграл!'
    return message
