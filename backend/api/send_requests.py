import logging
import os
import requests
import json

from django.core.cache import cache
from dotenv import load_dotenv
from rest_framework import status

from .exceptions import SendRequestException, TokenReceivingException
from .send_message import SendMessage
from orders.models import Order, OrderDetail, TypeStatusOrders

load_dotenv()

SUPPLIER_ID = os.getenv('SUPPLIER_ID')
PORTAL = os.getenv('PORTAL')
LOGIN_PORTAL = os.getenv('LOGIN_PORTAL')
PASSWORD_PORTAL = os.getenv('PASSWORD_PORTAL')
LOGIN_ENDPOINT = '/login'
TIME_TOKEN = 600
CHUNK_CONTROL_SINGL = 0
PROCESSING_TYPE_ALL = 0
HEADERS = {'Content-type': 'application/json'}
PORTAL_B24 = os.getenv('PORTAL_B24')
TOKEN_B24 = os.getenv('TOKEN_B24')
USER_B24 = os.getenv('USER_B24')
SHIPPING_COMPANY = os.getenv('SHIPPING_COMPANY')
TYPE_VYBEERAI = 1  # Add type marketplace
ENDPOINT_SEND_ORDER = 'crm.deal.add'
ENDPOINT_SEND_ORDER_PRODUCT = 'crm.deal.productrows.set'
ENDPOINT_DEL_ORDER = 'crm.deal.delete'
WAREHOUSES_B24 = {1: 597, 2: 599, 3: 601, 4: 603}  # 1-Nsk, 2-Spb, 3-Kdr, 4-Msk


class SendRequest:
    """Class for send request."""

    logger = logging.getLogger(__name__)

    @staticmethod
    def send_request_method(endpoint, data, portal=PORTAL, headers=HEADERS,
                            http_method='post'):
        """Send request."""
        if http_method == 'post':
            return requests.post(f'{portal}{endpoint}', data=data,
                                 headers=headers)
        elif http_method == 'get':
            return requests.get(f'{portal}{endpoint}', headers=headers)
        raise Exception('http method not allowded')

    @staticmethod
    def get_token(endpoint=LOGIN_ENDPOINT, username=LOGIN_PORTAL,
                  password=PASSWORD_PORTAL):
        """Get token."""
        SendRequest.logger.debug('Start get token')
        token = cache.get('token')
        if token:
            return token
        data = {'login': username, 'password': password}
        response = SendRequest.send_request_method(endpoint, json.dumps(data))
        status_code = response.status_code
        if status_code == status.HTTP_200_OK:
            token = response.text
            cache.set('token', token, TIME_TOKEN)
            return token
        try:
            r_text = response.json()
        except Exception:
            r_text = response.text
        error_log = (f'Receiving token error. Status code: `{status_code}`. '
                     f'{r_text}')
        SendRequest.logger.critical(error_log)
        SendMessage.send_message(error_log)
        raise TokenReceivingException(f'Receiving token error {status_code}')

    @staticmethod
    def send_request_token(endpoint, data, supplierId=SUPPLIER_ID,
                           chunkControl=CHUNK_CONTROL_SINGL,
                           processingType=PROCESSING_TYPE_ALL,
                           http_method='post'):
        """Send request token."""
        try:
            token = SendRequest.get_token()
        except TokenReceivingException as e:
            raise e

        headers = {'Authorization': f'Bearer {token}'}
        params = {}
        if http_method == 'post':
            headers = HEADERS | headers
            if endpoint == '/SyncOrder/syncOrders':
                params = {
                    'supplierId': supplierId,
                    'orders': data
                }
            else:
                params = {
                    'supplierId': supplierId,
                    'chunkControl': chunkControl,
                    'processingType': processingType,
                    'data': data
                }
        request_info = (f'endpoint: {endpoint}, headers: {headers}, '
                        f'params: {params}')
        request_info = request_info.replace(token, 'token')
        SendRequest.logger.debug(f'Start send request {request_info}')
        response = SendRequest.send_request_method(
            endpoint, json.dumps(params), headers=headers,
            http_method=http_method,
        )
        status_code = response.status_code
        try:
            r_text = response.json()
        except Exception:
            r_text = response.text
        if status_code == status.HTTP_200_OK:
            if endpoint == '/SyncOrder/syncOrders':
                for order_no in data:
                    order = Order.objects.get(orderNo=order_no)
                    order.status = TypeStatusOrders.CONFIRMED
                    order.save()
            return r_text
        error_log = (f'Error send request. Status code: `{status_code}`. '
                     f'{r_text}')
        SendRequest.logger.critical(error_log)
        SendMessage.send_message(error_log)
        raise SendRequestException(f'Error send request {status_code}')

    @staticmethod
    def send_orders_b24():
        orders = Order.objects.filter(status=TypeStatusOrders.RECEIVED)
        for order in orders:
            if order.code_B24 is None or order.code_B24 == 0:
                rq_text = (f'fields[TITLE]=Выбирай заказ №{order.orderNo}'
                           f'&fields[TYPE_ID]={TYPE_VYBEERAI}'
                           '&fields[CATEGORY_ID]=0'
                           '&fields[STAGE_ID]=NEW'
                           f'&fields[ASSIGNED_BY_ID]={USER_B24}'
                           f'&fields[UF_CRM_1659326670]='
                           f'{WAREHOUSES_B24.get(order.warehouse.pk)}'
                           '&fields[TAX_VALUE]=0.0'
                           f'&fields[UF_CRM_1650617036]={SHIPPING_COMPANY}'
                           f'&fields[COMMENTS]='
                           f'Расчет: {order.operation.operationName}\n'
                           f'Дата заказа: {str(order.creationDate)}\n'
                           f'Дата доставки: {str(order.deliveryDate)}\n'
                           f'{order.comment}')
                # f'&fields[BEGINDATE]={str(.creationDate).replace(" ", "T")}'
                # f'&fields[CLOSEDATE]={str(.deliveryDate).replace(" ", "T")}'
                #  '&fields[COMPANY_ID]=0&fields[CONTACT_ID]=0'
                print(rq_text)
                response = SendRequest.send_request_method(
                    f'{ENDPOINT_SEND_ORDER}?{rq_text}',
                    {}, portal=f'{PORTAL_B24}{TOKEN_B24}',
                    headers={},
                    http_method='get',
                )
                status_code = response.status_code
                if status_code == status.HTTP_200_OK:
                    order_code_B24 = response.json()['result']
                    products = OrderDetail.objects.filter(order=order)
                    rq_text_product = f'id={order_code_B24}'
                    i = 1
                    for product in products:
                        rq_text_product += (
                            f'&rows[{i}][PRODUCT_ID]='
                            f'{product.product.codeBitrix}'
                            f'&rows[{i}][QUANTITY]={product.qty}'
                            f'&rows[{i}][PRICE]={product.price}'
                            f'&rows[{i}][TAX_INCLUDED]=Y'
                            f'&rows[{i}][TAX_RATE]=0'
                            f'&rows[{i}][MEASURE_CODE]='
                            f'{product.product.package.package_code}'
                            f'&rows[{i}][MEASURE_NAME]='
                            f'{product.product.package.packageName}'
                            #  f'&rows[{i}][PRODUCT_NAME]=name'
                            #  f'&rows[{i}][PRICE_EXCLUSIVE]={product.price}'
                            #  f'&rows[{i}][PRICE_NETTO]={product.price}'
                            #  f'&rows[{i}][PRICE_BRUTTO]={product.price}'
                            #  f'&rows[{i}][DISCOUNT_TYPE_ID]=2'
                            #  f'&rows[{i}][DISCOUNT_RATE]=0'
                            #  f'&rows[{i}][DISCOUNT_SUM]=0]'
                            f'&rows[{i}][CUSTOMIZED]=Y')
                        i += 1
                    response_product = SendRequest.send_request_method(
                        f'{ENDPOINT_SEND_ORDER_PRODUCT}?{rq_text_product}',
                        {}, portal=f'{PORTAL_B24}{TOKEN_B24}',
                        headers={},
                        http_method='get',
                    )
                    status_code_product = response_product.status_code
                    if status_code_product == status.HTTP_200_OK:
                        order.code_B24 = order_code_B24
                        order.status = TypeStatusOrders.SEND_B24
                        order.save()
                    else:
                        SendRequest.send_request_method(
                            f'{ENDPOINT_DEL_ORDER}?ID={order_code_B24}',
                            {}, portal=f'{PORTAL_B24}{TOKEN_B24}',
                            headers={},
                            http_method='get',
                        )
                        error_log = (f'Error send request B24 Order product. '
                                     'Status code: '
                                     f'`{status_code}`. {response.json()}')
                        SendRequest.logger.critical(error_log)
                        SendMessage.send_message(error_log)
                        raise SendRequestException(
                            f'Error send request B24 {status_code}'
                        )
                else:
                    error_log = (f'Error send request B24 Order. Status code: '
                                 f'`{status_code}`. {response.json()}')
                    SendRequest.logger.critical(error_log)
                    SendMessage.send_message(error_log)
                    raise SendRequestException(
                        f'Error send request B24 {status_code}'
                    )
            else:
                ...
                #  Code B24 exist, but status not sender
        return 'Orders load'  # Add info about orders
