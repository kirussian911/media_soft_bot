import pyowm
import logging
from logging import getLogger

from telegram import Bot, Update
from telegram import (ParseMode, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove,
                      KeyboardButton, ReplyKeyboardMarkup)

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

from telegram_bot.config import TG_TOKEN, TG_API_URL
from telegram_bot.config import API_Key_Weather

from telegram_bot.buttons import get_base_reply_keyboard
from telegram_bot.logging import debug_requests

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

BUTTON_HELP = "Помощь"

CALLBACK_BUTTON_HIDE_KEYBOARD = "callback_button_hide"
TITLES = {CALLBACK_BUTTON_HIDE_KEYBOARD: "Спрять клавиатуру", }


@debug_requests
def get_base_reply_keyboard():
    keyboard = [[KeyboardButton(BUTTON_HELP), ], ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
    )


@debug_requests
def get_base_inline_keyboard():
    """ Получить клавиатуру для сообщения
        Эта клавиатура будет видна под каждым сообщением, где её прикрепили
    """
    keyboard = [
        [InlineKeyboardButton(TITLES[CALLBACK_BUTTON_HIDE_KEYBOARD], callback_data=CALLBACK_BUTTON_HIDE_KEYBOARD), ],
    ]
    return InlineKeyboardMarkup(keyboard)


@debug_requests
def keyboard_callback_handler(update: Update, context, **kwargs):
    """ Обработчик ВСЕХ кнопок со ВСЕХ клавиатур """
    query = update.callback_query
    data = query.data

    update.callback_query.message.edit_text

    chat_id = update.effective_message.chat_id
    current_text = update.effective_message.text

    if data == CALLBACK_BUTTON_HIDE_KEYBOARD:
        # Спрятать клавиатуру
        context.bot.send_message(
            chat_id=chat_id,
            text="Спрятали клавиатуру\n\nНажмите /start чтобы вернуть её обратно",
            reply_markup=ReplyKeyboardRemove(),
        )


def do_start(update: Update, context) -> str:
    """Обработчик стартового вызова"""
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Привет! Напиши город, погоду в котором ты хотел бы узнать",
        reply_markup=get_base_reply_keyboard(),
    )


@debug_requests
def do_help(update: Update, context):
    """Обрабатывает обращение юзера к функции help"""
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Это учебный бот для MediaSoft\n\n"
             "1. Узнать погоду: нажми /start и напиши город\n"
             "2. Транслит. Пример запроса: /translate Привет\n",
        reply_markup=get_base_inline_keyboard(),
    )


def do_weather(update: Update, context) -> str:
    """ Принимаем запрос и возвращаем погоду"""
    owm = pyowm.OWM(API_Key_Weather)
    text_location = update.message.text
    observation = owm.weather_at_place(text_location)
    w = observation.get_weather()
    humidity = w.get_humidity()
    wind = w.get_wind()
    temp = w.get_temperature('celsius')
    convert_temp = str(temp.get('temp'))
    convert_wind = str(wind.get('speed'))
    convert_humidity = str(humidity)
    response = update.message.reply_text(f'Температура: {convert_temp} C \nСкорость ветра: {convert_wind} м/с '
                                         f'\nВлажность воздуха: {convert_humidity}%')

    return response


@debug_requests
def do_translate(update: Update, context) -> str:
    """Принимает запрос и переводит текст в транслитерацию"""

    cyrillic = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    latin = 'a|b|v|g|d|e|e|zh|z|i|i|k|l|m|n|o|p|r|s|t|u|f|kh|tc|ch|sh|shch||y||e|iu|' \
            'ia|A|B|V|G|D|E|E|Zh|Z|I|I|K|L|M|N|O|P|R|S|T|U|F|Kh|Tc|Ch|Sh|Shch||Y||E|Iu|Ia'.split('|')

    word_for_translate = update.message.text.translate({ord(k): v for k, v in zip(cyrillic, latin)})
    response = update.message.reply_text(word_for_translate.split('/translate ')[1])

    return response


@debug_requests
def do_echo(update: Update, context):
    """Вызываем определенную функцию в зависимости от действий юзера"""
    chat_id = update.message.chat_id
    text = update.message.text

    if text == BUTTON_HELP:
        return do_help(update=update, context=context)
    if text in ['/translate']:
        return do_translate(update=update, context=context)
    else:
        return do_weather(update=update, context=context)


def main():
    logger.info("Запускаем бота...")

    updater = Updater(token=TG_TOKEN, use_context=True, base_url=TG_API_URL)
    dispatcher = updater.dispatcher

    # Прописываем все варианты запуска команд
    start_handler = CommandHandler("start", do_start)
    help_handler = CommandHandler("help", do_help)
    weather_handler = CommandHandler("weather", do_weather)
    translate_handler = CommandHandler("translate", do_translate)
    message_handler = MessageHandler(Filters.text, do_echo)
    buttons_handler = CallbackQueryHandler(callback=keyboard_callback_handler)

    #Добавляем в диспечтер все команды
    updater.dispatcher.add_handler(start_handler)
    updater.dispatcher.add_handler(help_handler)
    updater.dispatcher.add_handler(weather_handler)
    updater.dispatcher.add_handler(message_handler)
    updater.dispatcher.add_handler(translate_handler)
    updater.dispatcher.add_handler(buttons_handler)

    # Начать обработку входящих сообщений
    updater.start_polling(timeout=2)
    # Не прерывать скрипт до обработки всех сообщений
    updater.idle()

    logger.info("Закончили... Спасибо MediaSoft за курс Python!")


if __name__ == '__main__':
    main()
