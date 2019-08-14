from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup


def get_base_reply_keyboard():
    keyboard = [[KeyboardButton(BUTTON_HELP),],]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
    )