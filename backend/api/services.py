import logging
import os

import telegram
from dotenv import load_dotenv

from .exceptions import NotFoundDataException, NotFoundEndpointException
from warehouses.models import Warehouse

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

ENDPOINTS = {
    'productWarehouses': '/Warehouse/productWarehouses/',
    'loadProduct': '/Product/loadProduct/',
}


def get_data(way):
    """Get data for request."""
    data = []
    if way == 'productWarehouses':
        for warehouse in Warehouse.objects.all():
            data.append({
                'warehouseExternalCode': warehouse.warehouseExternalCode,
                'customerExternalCode': warehouse.customerExternalCode,
                'warehouseName': warehouse.warehouseName,
                'status': '2',
            })
    elif way == 'loadProduct':
        data.append({'key': 'value'})
    if data:
        return data
    raise NotFoundDataException(f'Not found data for {way}')


def get_endpoint_data(way):
    """Get endpoint and data."""
    try:
        endpoint_data = (ENDPOINTS[way], get_data(way))
    except KeyError:
        raise NotFoundEndpointException(f'Not found endpoint for {way}')
    except NotFoundDataException as e:
        raise e
    return endpoint_data


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
