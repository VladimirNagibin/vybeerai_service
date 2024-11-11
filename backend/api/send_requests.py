import logging
import os
import requests
import json

from django.core.cache import cache
from dotenv import load_dotenv
from rest_framework import status

from .exceptions import SendRequestException, TokenReceivingException
from .services import SendMessage

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


class SendRequest:
    """Class for send request."""

    logger = logging.getLogger(__name__)

    @staticmethod
    def send_request_post(endpoint, data, portal=PORTAL, headers=HEADERS):
        """Send request."""
        return requests.post(f'{portal}{endpoint}', data=data, headers=headers)

    @staticmethod
    def get_token(endpoint=LOGIN_ENDPOINT, username=LOGIN_PORTAL,
                  password=PASSWORD_PORTAL):
        """Get token."""
        SendRequest.logger.debug('Start get token')
        token = cache.get('token')
        if token:
            return token
        data = {'login': username, 'password': password}
        response = SendRequest.send_request_post(endpoint, json.dumps(data))
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
                           processingType=PROCESSING_TYPE_ALL):
        """Send request token."""
        try:
            token = SendRequest.get_token()
        except TokenReceivingException as e:
            raise e
        headers = HEADERS | {'Authorization': f'Bearer {token}'}
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
        response = SendRequest.send_request_post(
            endpoint, json.dumps(params), headers=headers
        )
        status_code = response.status_code
        if status_code == status.HTTP_200_OK:
            return response.json()
        error_log = (f'Error send request. Status code: `{status_code}`. '
                     f'{response.json()}')
        SendRequest.logger.critical(error_log)
        SendMessage.send_message(error_log)
        raise SendRequestException(f'Error send request {status_code}')
