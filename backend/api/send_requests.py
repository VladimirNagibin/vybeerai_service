import logging
import os
import sys
import requests
import json
from logging.handlers import RotatingFileHandler

from django.core.cache import cache
from dotenv import load_dotenv
from rest_framework import status

from .exceptions import SendRequestException, TokenReceivingException
from .services import send_message
from warehouses.models import Warehouse

load_dotenv()

SUPPLIER_ID = os.getenv('SUPPLIER_ID')
PORTAL = os.getenv('PORTAL')
LOGIN_PORTAL = os.getenv('LOGIN_PORTAL')
PASSWORD_PORTAL = os.getenv('PASSWORD_PORTAL')
LOGIN_ENDPOINT = '/login/'
TIME_TOKEN = 600


class SendRequest:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            ('%(asctime)s - %(name)s - %(funcName)s - %(lineno)s - %(levelname)s - '
             '%(message)s')
        )
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setFormatter(formatter)
        file_handler = RotatingFileHandler(
            f'{__file__}.log', maxBytes=50000, backupCount=3, encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.addHandler(file_handler)

    @staticmethod
    def send_request(endpoint, data, portal=PORTAL,
                     headers={'Content-type': 'application/json'}):
        """Send request."""
        return requests.post(f'{portal}{endpoint}', data=data, headers=headers)

    def get_token(self, endpoint=LOGIN_ENDPOINT, username=LOGIN_PORTAL,
                  password=PASSWORD_PORTAL):
        """Get token."""
        self.logger.debug('Start get token')
        token = cache.get('token')
        if token:
            return token
        data = {'username': username, 'password': password}
        response = SendRequest.send_request(endpoint, json.dumps(data))
        status_code = response.status_code
        if status_code == status.HTTP_200_OK:
            token = response.json()
            cache.set('token', token, TIME_TOKEN)
            return token
        error_log = (f'Receiving token error. Status code: `{status_code}`. '
                     f'{response.json()}')
        self.logger.exception(error_log)
        send_message(error_log)
        raise TokenReceivingException(f'Receiving token error {status_code}')

    def send_request_token(self, endpoint, data, supplierId=SUPPLIER_ID,
                           chunkControl=0, processingType=0, status_=2):
        """Send request token."""
        try:
            token = self.get_token()
        except TokenReceivingException as e:
            raise e
        headers = {'Content-type': 'application/json',
                   'Authorization': f'Bearer {token}'}
        params = {
            'supplierId': supplierId,
            'chunkControl': chunkControl,
            'processingType': processingType,
            'status': status_,
            'data': data
        }
        request_info = (f'endpoint: {endpoint}, headers: {headers}, '
                        f'params: {params}')
        request_info = request_info.replace(token, 'token')
        self.logger.debug(f'Start send request {request_info}')
        response = SendRequest.send_request(
            endpoint, json.dumps(params), headers=headers
        )
        status_code = response.status_code
        if status_code == status.HTTP_200_OK:
            return response.json()
        error_log = (f'Error send request. Status code: `{status_code}`. '
                     f'{response.json()}')
        self.logger.exception(error_log)
        send_message(error_log)
        raise SendRequestException(f'Error send request {status_code}')

    def product_warehouses(self, endpoint='/Warehouse/productWarehouses/',):
        """Synchronization warehouses."""
        data = []
        for warehouse in Warehouse.objects.all():
            data.append({
                'warehouseExternalCode': warehouse.warehouseExternalCode,
                'customerExternalCode': warehouse.customerExternalCode,
                'warehouseName': warehouse.warehouseName,
                'status': '2',
            })
        try:
            response = self.send_request_token(endpoint, data)
            # return response.json()
            # print(type(response))
            return response
        except TokenReceivingException as e:
            print(e)
        except SendRequestException as e:
            print(e)
        except Exception as e:
            print(e)
