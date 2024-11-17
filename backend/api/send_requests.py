import logging
import os
import requests
import json

from django.core.cache import cache
from dotenv import load_dotenv
from rest_framework import status

from .exceptions import SendRequestException, TokenReceivingException
from .send_message import SendMessage
from orders.models import Order, TypeStatusOrders

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
        error_log = (f'Receiving token error. Status code: `{status_code}`. '
                     f'{response.json()}')
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
            if endpoint == 'syncOrder/syncOrders':
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
        if status_code == status.HTTP_200_OK:
            return response.json()
        error_log = (f'Error send request. Status code: `{status_code}`. '
                     f'{response.json()}')
        SendRequest.logger.critical(error_log)
        SendMessage.send_message(error_log)
        raise SendRequestException(f'Error send request {status_code}')

    @staticmethod
    def send_orders_b24():

        orders = Order.objects.filter(status=TypeStatusOrders.RECEIVED)
        for order in orders:
            if order.code_B24 is None:
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
            # f'&fields[BEGINDATE]={str(order.creationDate).replace(" ", "T")}'
            # f'&fields[CLOSEDATE]={str(order.deliveryDate).replace(" ", "T")}'
            #  '&fields[COMPANY_ID]=0&fields[CONTACT_ID]=0'
            response = SendRequest.send_request_method(
                f'{ENDPOINT_SEND_ORDER}?{rq_text}',
                {}, portal=f'{PORTAL_B24}{TOKEN_B24}',
                headers={},
                http_method='get',
            )
            status_code = response.status_code
            if status_code == status.HTTP_200_OK:
                # Load products
                order.code_B24 = response.json()['result']
                order.status = TypeStatusOrders.SEND_B24
                order.save()
            else:
                error_log = (f'Error send request B24. Status code: '
                             f'`{status_code}`. {response.json()}')
                SendRequest.logger.critical(error_log)
                SendMessage.send_message(error_log)
                raise SendRequestException(
                    f'Error send request B24 {status_code}'
                )
