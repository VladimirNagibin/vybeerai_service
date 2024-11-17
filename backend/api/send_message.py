import logging
import os

import telegram
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


class SendMessage:
    """Class for send message."""

    logger = logging.getLogger(__name__)

    @staticmethod
    def send_message(message):
        """Send message in Telegram."""
        SendMessage.logger.debug(f'Bot start send message: `{message}`')
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        try:
            bot.send_message(TELEGRAM_CHAT_ID, message)
        except telegram.error.TelegramError as error:
            SendMessage.logger.exception(
                f'Error send message `{message}` in Telegram: {error}'
            )
            return False
        SendMessage.logger.debug(f'Bot send message: `{message}`')
        return True
