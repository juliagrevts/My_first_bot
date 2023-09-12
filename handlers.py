from glob import glob
import os
from random import choice

import ephem

from utils import (
    get_smile,
    has_object_on_image,
    main_keyboard,
    play_random_numbers,
    precalculate,
    set_cities_set
)


def greet_user(update, context):
    print('Вызван /start')
    smile = get_smile(context.user_data)
    if 'bot_cities' not in context.user_data:
        set_cities_set(context)
    first_name = update.effective_user.first_name
    update.message.reply_text(
        f'Привет, {first_name}!{smile}',
        reply_markup=main_keyboard()
    )


def name_constellation(update, context):
    user_input = update.message.text.split()
    if len(user_input) > 2:
        message = 'Нужно передать только одну планету'
    else:
        user_planet = user_input.pop().capitalize()
        try:
            planet_name = getattr(ephem, user_planet)
            planet = planet_name()
            planet.compute()
            constellation = ephem.constellation(planet)
            message = f'Планета сейчас находится в созвездии {constellation}'
        except AttributeError:
            message = 'Бот не знает такую планету'
    update.message.reply_text(message, reply_markup=main_keyboard())


def count_words(update, context):
    user_input = update.message.text.split()
    len_user_input = len(user_input) - 1
    update.message.reply_text(
        f'{len_user_input} слов', reply_markup=main_keyboard()
    )


def determine_full_moon(update, context):
    user_input = update.message.text.split()
    # There should be a date in the 'year/month/date' format
    user_date_string = user_input.pop()
    update.message.reply_text(
        f'Ближайшее полнолуние {ephem.next_full_moon(user_date_string)}',
        reply_markup=main_keyboard()
    )


def play_cities(update, context):
    if 'bot_cities' not in context.user_data:
        set_cities_set(context)
    bot_cities = context.user_data['bot_cities']
    user_cities = context.user_data['user_cities']
    if context.args:
        user_city = ' '.join(context.args)
        if user_city not in user_cities:
            user_cities.add(user_city)
            if user_city in bot_cities:
                bot_cities.remove(user_city)
            found_city = False
            for city in bot_cities:
                if user_city[-1].capitalize() == city[0]:
                    update.message.reply_text(f'{city}, ваш ход')
                    bot_cities.remove(city)
                    found_city = True
                    break
                elif user_city[-1] == 'ь' or user_city[-1] == 'ы':
                    if user_city[-2].capitalize() == city[0]:
                        update.message.reply_text(f'{city}, ваш ход')
                        bot_cities.remove(city)
                        found_city = True
                        break
            if not found_city:
                update.message.reply_text(
                    f'Не знаю городов на "{user_city[-1]}", ты выиграл!',
                    reply_markup=main_keyboard()
                )
                set_cities_set(context)
        else:
            update.message.reply_text(
                'Ты уже называл этот город',
                reply_markup=main_keyboard()
            )
    else:
        update.message.reply_text(
            'Ты не ввел город после /cities',
            reply_markup=main_keyboard()
        )


def calculate(update, context):
    user_input = update.message.text.split('/calc')
    user_input = user_input[1].replace(' ', '')
    if len(user_input) >= 3:
        try:
            parts = user_input.split('+')
            for i in range(len(parts)):
                if '-' in parts[i]:
                    parts[i] = parts[i].split('-')
            for i in range(len(parts)):
                parts[i] = precalculate(parts[i])
            result = sum(parts)
        except ValueError:
            result = 'Видимо, ты что-то не то передал'
        except ZeroDivisionError:
            result = 'Нельзя делить на ноль!'
    else:
        result = 'Нужно передать минимум 2 числа и знак действия'
    update.message.reply_text(result, reply_markup=main_keyboard())


def talk_to_me(update, context):
    text = update.message.text
    smile = get_smile(context.user_data)
    # Take the first name of the current user
    first_name = update.effective_user.first_name
    update.message.reply_text(
        f'Привет, {first_name}!{smile} Ты написал: {text}',
        reply_markup=main_keyboard()
    )


def guess_number(update, context):
    if context.args:  # List of args the user passed after '/command '
        try:
            user_int = int(context.args[0])
            message = play_random_numbers(user_int)
        except (TypeError, ValueError):
            message = 'Введите целое число'
    else:
        message = 'Введите число после команды /guess'
    # Reply to the chat that wrote to the bot
    update.message.reply_text(message, reply_markup=main_keyboard())


def send_elephant_picture(update, context):
    elephant_pics_list = glob('images/el*.jpg')
    elephant_pic_path = choice(elephant_pics_list)
    # Take the current chat id
    chat_id = update.effective_chat.id
    context.bot.send_photo(
        # When sending an image, you need to specify the chat_id explicitly
        chat_id=chat_id,
        photo=open(elephant_pic_path, 'rb'),
        reply_markup=main_keyboard()
    )


def user_location(update, context):
    smile = get_smile(context.user_data)
    coords = update.message.location
    update.message.reply_text(
        f'Ваши координаты {coords} {smile}',
        reply_markup=main_keyboard()
    )


def check_user_photo(update, context):
    update.message.reply_text('Обрабатываю фото')
    # Create a new dir if it doesn't exist otherwise do nothing
    os.makedirs('downloads', exist_ok=True)
    # Take the biggest size file
    user_photo = context.bot.getFile(update.message.photo[-1].file_id)
    # Create a filename and download the file
    file_name = os.path.join('downloads', f'{user_photo.file_id}.jpg')
    user_photo.download(file_name)

    if has_object_on_image(file_name, object_name='elephant'):
        new_file_name = os.path.join('images', f'el_{user_photo.file_id}.jpg')
        os.rename(file_name, new_file_name)
        update.message.reply_text('На твоем фото есть слоник, сохранил его')
    else:
        os.remove(file_name)
        update.message.reply_text('На этом фото слоник не найден')
