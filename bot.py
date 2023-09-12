import logging

from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from handlers import (
    calculate,
    check_user_photo,
    count_words,
    determine_full_moon,
    greet_user,
    guess_number,
    name_constellation,
    play_cities,
    send_elephant_picture,
    talk_to_me,
    user_location
)
import settings


logging.basicConfig(
    filename='bot.log',
    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
    level=logging.INFO
)


def main():
    mybot = Updater(settings.API_KEY, use_context=True)

    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(CommandHandler('planet', name_constellation))
    dp.add_handler(CommandHandler('wordcount', count_words))
    dp.add_handler(CommandHandler('fullmoon', determine_full_moon))
    dp.add_handler(CommandHandler('cities', play_cities))
    dp.add_handler(CommandHandler('calc', calculate))
    dp.add_handler(CommandHandler('guess', guess_number))

    dp.add_handler(MessageHandler(Filters.photo, check_user_photo))
    dp.add_handler(MessageHandler(Filters.location, user_location))
    dp.add_handler(MessageHandler(Filters.regex('^Пришли фото слоника$'), send_elephant_picture))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))

    logging.info('Бот стартовал')
    mybot.start_polling()
    mybot.idle()


if __name__ == "__main__":
    main()
