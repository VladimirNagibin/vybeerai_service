import logging
import os

import telegram
from dotenv import load_dotenv

from .exceptions import NotFoundDataException, NotFoundEndpointException
from orders.models import (DeliveryDate, OperationOutlet, OutletPayForm,
                           PriceList)
from products.models import Product, ProductAttributValue
from warehouses.models import ProductStock, Warehouse

STATUS_CHANGE_OR_UPDATE = 2

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

ENDPOINTS = {
    'productWarehouses': '/Warehouse/productWarehouses/',
    'loadProduct': '/Product/loadProduct/',
    'loadProductAttributs': '/Product/loadProductAttributs/',
    'productStocks': '/Warehouse/productStocks/',
    'outletWarehouses': '/Warehouse/outletWarehouses/',
    'operations': '/Order/operations/',
    'deliveryDates': '/Order/deliveryDates/',
    'payForms': '/PayForm/payForms/',
    'outletPayForms': '/PayForm/outletPayForms/',
    'priceLists': '/PayForm/priceLists/',
}


def get_data(way, status=STATUS_CHANGE_OR_UPDATE):
    """Get data for request."""
    data = []
    if way == 'productWarehouses':
        for warehouse in Warehouse.objects.all():
            data.append({
                'warehouseExternalCode': warehouse.warehouseExternalCode,
                'customerExternalCode': warehouse.customerExternalCode,
                'warehouseName': warehouse.warehouseName,
                'status': status,
            })
    elif way == 'loadProduct':
        productClassificationCode = 1
        for product in Product.objects.filter(active=True):
            data.append({
                'productExternalCode': product.productExternalCode,
                'productName': product.productName,
                'productClassificationExternalCode':
                f'{productClassificationCode}',
                'volume': product.volume,
                'package': product.package.packageName,
                'packageQty': product.packageQty,
                'description': product.description,
                'isTare': 1 if product.isTare else 0,
                'pictograph': product.pictograph.pictograph,
                'productsMix': [],
                'productsAnalog': [],
                'status': status,
            })
    elif way == 'loadProductAttributs':
        for product in Product.objects.filter(active=True):
            attributs = []
            for product_attribut_value in ProductAttributValue.objects.filter(
                product=product
            ):
                attributs.append({
                    'attributsName': product_attribut_value
                    .attributValue
                    .attribut
                    .attributsName,
                    'attributsNameSortOrder': product_attribut_value
                    .attributValue
                    .attribut
                    .attributsNameSortOrder,
                    'isFilter': (1 if product_attribut_value.
                                 attributValue.attribut.isFilter else 0),
                    'isCardDetailsProduct': (1 if product_attribut_value
                                             .attributValue.attribut
                                             .isCardDetailsProduct else 0),
                    'attributsValue': product_attribut_value
                    .attributValue
                    .attributsValue,
                    'attributsValueSortOrder': product_attribut_value
                    .attributValue
                    .attributsValueSortOrder,
                    'status': status,
                })
            data.append({
                'productExternalCode': product.productExternalCode,
                'productsAttributsValue': attributs,
            })
    elif way == 'productStocks':
        for product_stock in ProductStock.objects.filter(product__active=True):
            data.append({
                'warehouseExternalCode': product_stock.warehouse
                .warehouseExternalCode,
                'customerExternalCode': product_stock.warehouse
                .customerExternalCode,
                'productExternalCode': product_stock.product
                .productExternalCode,
                'stock': product_stock.stock,
                'status': status,
            })
    elif way == 'outletWarehouses':
        for warehouse in Warehouse.objects.all():
            data.append({
                'outletExternalCode': warehouse.outlet.outletExternalCode,
                'warehouseExternalCode': warehouse.warehouseExternalCode,
                'customerExternalCode': warehouse.customerExternalCode,
                'status': status,
            })
    elif way == 'operations':
        for operation in OperationOutlet.objects.all():
            data.append({
                'outletExternalCode': operation
                .warehouse
                .outlet
                .outletExternalCode,
                'operationExternalCode': operation
                .operation
                .operationExternalCode,
                'operationName': operation
                .operation
                .operationName,
                'customerExternalCode': operation
                .warehouse
                .customerExternalCode,
                'coefficient': operation
                .operation
                .coefficient,
                'status': status,
            })
    elif way == 'deliveryDates':
        for delivery_date in DeliveryDate.objects.all():
            data.append({
                'outletExternalCode': delivery_date
                .warehouse
                .outlet
                .outletExternalCode,
                'customerExternalCode': delivery_date
                .warehouse
                .customerExternalCode,
                'deliveryDate': delivery_date.deliveryDate,
                'deadLine': delivery_date.deadLine,
                'minSum': delivery_date.minSum,
                'status': status,
            })
    elif way == 'outletPayForms':
        for pay_forms in OutletPayForm.objects.all():
            data.append({
                'outletExternalCode': pay_forms
                .warehouse
                .outlet
                .outletExternalCode,
                'payFormExternalCode': pay_forms.payForm.payFormExternalCode,
                'customerExternalCode': pay_forms
                .warehouse
                .customerExternalCode,
                'status': status,
            })
    elif way == 'payForms':
        for pay_forms in OutletPayForm.objects.all():
            data.append({
                'payFormExternalCode': pay_forms.payForm.payFormExternalCode,
                'payFormName': pay_forms.payForm.payFormName,
                'vatCalculationMode': (1
                                       if pay_forms.payForm.vatCalculationMode
                                       else 0),
                'customerExternalCode': pay_forms
                .warehouse
                .customerExternalCode,
                'orderTypeExternalCode': pay_forms
                .payForm
                .orderTypeExternalCode,
                'status': status,
            })
    elif way == 'priceLists':
        for price_list in PriceList.objects.filter(product__active=True):
            data.append({
                'payFormExternalCode': price_list.payForm.payFormExternalCode,
                'customerExternalCode': price_list
                .warehouse
                .customerExternalCode,
                'productExternalCode': price_list.product.productExternalCode,
                'productType': price_list.productType,
                'price': price_list.price,
                'vat': price_list.vat,
                'status': status,
            })
    if data:
        return data
    raise NotFoundDataException(f'Not found data for {way}')


def get_endpoint_data(way, status=STATUS_CHANGE_OR_UPDATE):
    """Get endpoint and data."""
    try:
        endpoint_data = (ENDPOINTS[way], get_data(way, status))
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
