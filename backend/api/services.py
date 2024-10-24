import logging
import os

import telegram
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def send_message(message):
    """Отправка сообщения в Telegram."""
    # logger.debug(f'Бот начал отправку сообщения: `{message}`')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.error.TelegramError as error:
    #    logger.exception(
    #        f'Ошибка отправки сообщения `{message}` в Telegram: {error}'
    #    )
        return False
    # logger.debug(f'Бот отправил сообщение: `{message}`')
    return True
