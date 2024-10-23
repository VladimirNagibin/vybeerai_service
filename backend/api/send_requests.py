import os
import requests
import json

from dotenv import load_dotenv

load_dotenv()

SUPPLIER_ID = os.getenv('SUPPLIER_ID')
PORTAL = os.getenv('PORTAL')
LOGIN_PORTAL = os.getenv('LOGIN_PORTAL')
PASSWORD_PORTAL = os.getenv('PASSWORD_PORTAL')
LOGIN_ENDPOINT = '/login/'


class SendRequest:

    @staticmethod
    def send_request(endpoint, data, portal=PORTAL,
                     headers={'Content-type': 'application/json'}):
        """Send request."""
        return requests.post(f'{portal}{endpoint}', data=data, headers=headers)

    @staticmethod
    def get_token(endpoint=LOGIN_ENDPOINT, username=LOGIN_PORTAL,
                  password=PASSWORD_PORTAL):
        """Get token."""
        data = {'username': username, 'password': password}
        response = SendRequest.send_request(endpoint, json.dumps(data))
        status_code = response.status_code
        if status_code == 200:
            return response.json()
        return status_code

    @staticmethod
    def product_warehouses(endpoint='/Warehouse/productWarehouses/',):
        """Synchronization warehouses."""
        data = {'supplierId': SUPPLIER_ID, 'chunkControl': 0}
        token = SendRequest.get_token()
        headers = {'Content-type': 'application/json',
                   'Authorization': f'Bearer {token}'}
        print(headers)
        response = SendRequest.send_request(endpoint, json.dumps(data),
                                            headers=headers)
        status_code = response.status_code
        if status_code == 200:
            return response.json()
        return status_code
