import logging
import os
import requests
import json
import sys

from django.core.cache import cache
from dotenv import load_dotenv
from rest_framework import status

from .exceptions import (RequestB24Exception, SendRequestException,
                         TokenReceivingException)
from .send_message import SendMessage
from orders.models import Order, OrderDetail, TypeStatusOrders
from warehouses.models import Outlet, TypeStatusCompany

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
ENDPOINT_ADD_CONPANY = 'crm.company.add'
ENDPOINT_ADD_CONPANY_REQUIS = 'crm.requisite.add'
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
            #token = response.json()
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
                if not data:
                    return 'There are no Orders to send to Vybeerai'
                params = {
                    'supplierId': supplierId,
                    'orders': data
                }
            elif endpoint == '/set-real-external-code':
                params = data
            elif endpoint == '/close-outlet':
                params = data
            else:
                params = {
                    'supplierId': supplierId,
                    'chunkControl': chunkControl,
                    'processingType': processingType,
                    'data': data
                }
        request_info = (f'endpoint: {endpoint}, headers: {headers}, '
                        f'http method: {http_method}, '
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
                    order = Order.objects.get(orderNo=order_no['orderNo'])
                    order.status = TypeStatusOrders.CONFIRMED
                    order.save()
            elif endpoint == '/set-real-external-code':
                real_external_code = data['realExternalCode']
                outlet = Outlet.objects.get(
                    outletExternalCode=real_external_code
                )
                outlet.status = TypeStatusCompany.CONFIRMED
                outlet.save()
            return r_text
        error_log = (f'Error send request. Status code: `{status_code}`. '
                     f'{r_text}')
        SendRequest.logger.critical(error_log)
        SendMessage.send_message(error_log)
        raise SendRequestException(f'{error_log}')

    @staticmethod
    def send_request_B24(endpoint, param):
        try:
            response = SendRequest.send_request_method(
                        f'{endpoint}?{param}',
                        {}, portal=f'{PORTAL_B24}{TOKEN_B24}',
                        headers={},
                        http_method='get',
            )
        except Exception as e:
            return {'error': 'exception_request', 'error_description': e}
        return response.json()

    @staticmethod
    def normalization_phone(phone):
        phone = phone.strip()
        phone = phone.removeprefix('+')
        phone = phone.strip()
        phone = phone.removeprefix('7')
        phone = phone.removeprefix('8')
        phone = phone.replace(' ', '')
        phone = phone.replace('(', '')
        phone = phone.replace(')', '')
        phone = phone.replace('-', '')
        return phone

    @staticmethod
    def check_company_field(
        inn, legal_name, code_B24, delivery_address, contact_person,
        phone_company
    ):
        upd_company_result = {}
        # Check phone
        phone_upd = True
        i = 0
        endpoint = 'crm.company.get'
        param = f'id={code_B24}'
        response = SendRequest.send_request_B24(endpoint, param)
        if result := response.get('result'):
            if result['HAS_PHONE'] == 'Y':
                phones = result['PHONE']
                i = len(phones)
                phones_val = [
                    SendRequest.normalization_phone(phone['VALUE']) for phone in phones
                ]
                if SendRequest.normalization_phone(phone_company) in phones_val:
                    phone_upd = False
        if phone_upd:
            param += (f'&fields[PHONE][{i}][VALUE]={phone_company}'
                      f'&fields[PHONE][{i}][VALUE_TYPE]=WORK')
            response = SendRequest.send_request_B24(
                'crm.company.update', param
            )
            if response.get('error'):  # result = 'True' in success
                upd_company_result['upd_phone'] = 'error'

        # Check address
        if delivery_address:
            address_upd = True
            address_ids = {}
            ids_requisites = []
            endpoint = 'crm.requisite.list'
            param = f'filter[ENTITY_ID]={code_B24}&select[0]=ID'
            response = SendRequest.send_request_B24(endpoint, param)
            if result := response.get('result'):
                ids_requisites = [req['ID'] for req in result]
                for id_req in ids_requisites:
                    endpoint = 'crm.address.list'
                    param = (f'filter[ENTITY_ID]={id_req}&'
                             'filter[ENTITY_TYPE_ID]=8&'
                             'filter[TYPE_ID]=11&select[0]=ADDRESS_1')
                    response = SendRequest.send_request_B24(endpoint, param)
                    if result := response.get('result'):
                        address_ids[id_req] = result
                        address_val = [
                            address['ADDRESS_1'] for address in result
                        ]
                        if delivery_address in address_val:
                            address_upd = False
                            break
            if address_upd:
                endpoint = 'crm.address.add'
                id_req = None
                if ids_requisites:
                    id_req = ids_requisites[0]
                    address_deliver_B24 = address_ids.get(id_req)
                    if address_deliver_B24:
                        endpoint = 'crm.address.update'
                else:
                    # create requisite
                    legal_name = legal_name if legal_name else 'компании'
                    rq_req_text = (
                        f'fields[ENTITY_TYPE_ID]=4'
                        f'&fields[ENTITY_ID]={code_B24}'
                        f'&fields[NAME]=Реквизиты {legal_name}'
                        f'&fields[RQ_INN]={inn}'
                    )
                    if int(inn) > 10000000000:  # inn businessman
                        rq_req_text += '&fields[PRESET_ID]=3'
                    else:  # juridical person
                        rq_req_text += '&fields[PRESET_ID]=1'
                    response = SendRequest.send_request_B24(
                        ENDPOINT_ADD_CONPANY_REQUIS, rq_req_text
                    )
                    id_req = response.get('result')
                if id_req:
                    param = (f'fields[TYPE_ID]=11&fields[ENTITY_TYPE_ID]=8'
                             f'&fields[ENTITY_ID]={id_req}'
                             f'&fields[ADDRESS_1]={delivery_address}')
                    response = SendRequest.send_request_B24(endpoint, param)
                    if response.get('error'):  # result = 'True' in success
                        upd_company_result['upd_address'] = 'error'
                else:
                    upd_company_result['upd_address'] = 'error'

        # Check contact
        if contact_person:
            contact_upd = True
            endpoint = 'crm.company.contact.items.get'
            param = f'id={code_B24}'
            response = SendRequest.send_request_B24(endpoint, param)
            if result := response.get('result'):
                ids = [res['CONTACT_ID'] for res in result]
                for id in ids:
                    endpoint = 'crm.contact.get'
                    param = f'id={id}'
                    response = SendRequest.send_request_B24(endpoint, param)
                    if result := response.get('result'):
                        if result['NAME'] == contact_person:
                            contact_upd = False
                            break
        if contact_upd:
            param = (f'fields[ASSIGNED_BY_ID]={USER_B24}&'
                     f'fields[COMPANY_IDS][0]={code_B24}&'
                     f'fields[NAME]={contact_person}')
            response = SendRequest.send_request_B24('crm.contact.add', param)
            if response.get('error'):  # result = 'True' in success
                upd_company_result['upd_contact'] = 'error'
        return upd_company_result


    @staticmethod
    def check_company(inn, legal_name, code_B24, delivery_address,
                      contact_person, phone):
        endpoint_inn = (f'/crm.requisite.list?filter[RQ_INN]={inn}'
                        '&select[0]=ENTITY_TYPE_ID&select[1]=ENTITY_ID')
        customers_by_inn = SendRequest.send_request_method(
            endpoint_inn, {}, portal=f'{PORTAL_B24}{TOKEN_B24}',
            headers={},
            http_method='get',
        )
        status_code_inn = customers_by_inn.status_code
        if status_code_inn == status.HTTP_200_OK:
            result = (customers_by_inn.json().get('result'))
            if result is not None:
                inns = [res['ENTITY_ID'] for res in result]
                if code_B24:
                    if str(code_B24) in inns:
                        SendRequest.check_company_field(
                            inn, legal_name, code_B24, delivery_address, contact_person, phone
                        )
                        return code_B24
                    return 0
                else:
                    if len(result) == 1:
                        code_B24_B24 = result[0]['ENTITY_ID']
                        SendRequest.check_company_field(
                            inn, legal_name, code_B24_B24, delivery_address, contact_person,
                            phone
                        )
                        return code_B24_B24
                    elif len(result) > 1:
                        return None
                    else:
                        legal_name = legal_name if legal_name else f'Компания {inn}'
                        rq_text = (f'fields[ASSIGNED_BY_ID]={USER_B24}'
                                   f'&fields[TITLE]={legal_name}')
                        response = SendRequest.send_request_method(
                            f'{ENDPOINT_ADD_CONPANY}?{rq_text}',
                            {}, portal=f'{PORTAL_B24}{TOKEN_B24}',
                            headers={},
                            http_method='get',
                        )
                        status_code = response.status_code
                        if status_code == status.HTTP_200_OK:
                            company_code_B24 = response.json()['result']
                            legal_name = (
                                legal_name if legal_name else 'компании'
                            )
                            rq_req_text = (
                                f'fields[ENTITY_TYPE_ID]=4'
                                f'&fields[ENTITY_ID]={company_code_B24}'
                                f'&fields[NAME]=Реквизиты {legal_name}'
                                f'&fields[RQ_INN]={inn}'
                            )
                            if int(inn) > 10000000000:  # ind businessman
                                rq_req_text += '&fields[PRESET_ID]=3'
                            else:  # juridical person
                                rq_req_text += '&fields[PRESET_ID]=1'
                            response = SendRequest.send_request_method(
                                f'{ENDPOINT_ADD_CONPANY_REQUIS}?{rq_req_text}',
                                {}, portal=f'{PORTAL_B24}{TOKEN_B24}',
                                headers={},
                                http_method='get',
                            )
                            SendRequest.check_company_field(
                                inn, legal_name, company_code_B24,
                                delivery_address, contact_person, phone
                            )
                            return company_code_B24
                        raise RequestB24Exception(
                            f'INN: {inn}. bad request B24 add company'
                        )
            raise RequestB24Exception(
                f'INN: {inn}. bad request B24 get company by inn'
            )
        raise RequestB24Exception(
            f'INN: {inn}. bad request B24 get company by inn'
        )

    @staticmethod
    def send_orders_b24():
        result = {}
        orders = Order.objects.filter(status=TypeStatusOrders.RECEIVED)
        for order in orders:
            order_no = order.orderNo
            if order.code_B24 is None or order.code_B24 == 0:
                customer = order.outlet
                if customer:
                    code_B24 = customer.code_B24
                    delivery_address = customer.deliveryAddress
                    contact_person = customer.contactPerson
                    phone = customer.phone
                    comments = (f'Расчет: {order.operation.operationName}\n'
                                f'Телефон: {phone}\n'
                                f'Дата заказа: {str(order.creationDate)}\n'
                                f'Дата доставки: {str(order.deliveryDate)}\n')
                    comments += (f'Адрес доставки: {delivery_address}\n'
                                 if delivery_address else '')
                    comments += (f'Контактное лицо: {contact_person}\n'
                                 if contact_person else '')
                    comments += f'{order.comment}'
                    inn = customer.inn
                    legal_name = customer.legalName
                    try:
                        code_B24_B24 = SendRequest.check_company(
                            inn, legal_name, code_B24, delivery_address,
                            contact_person, phone
                        )
                    except (RequestB24Exception, Exception) as e:
                        raise SendRequestException(
                            f'Order No: {order_no}. Don"t create company. {e}'
                        )
                    if code_B24_B24 is None:
                        comments = ('В Битриксе существует больше '
                                    f'одной компании с ИНН {inn}. '
                                    'Выберите подходящую вручную.')
                        + comments
                    elif code_B24_B24 == 0:
                        comments = (f'У компании прописан код Б24 {code_B24}, '
                                    f'но ИНН {inn} не совпадает. '
                                    'Выберите компанию вручную.')
                        + comments
                rq_text = (f'fields[TITLE]=Выбирай заказ №{order_no}'
                           f'&fields[TYPE_ID]={TYPE_VYBEERAI}'
                           '&fields[CATEGORY_ID]=0'
                           '&fields[STAGE_ID]=NEW'
                           f'&fields[ASSIGNED_BY_ID]={USER_B24}'
                           f'&fields[UF_CRM_1659326670]='
                           f'{WAREHOUSES_B24.get(order.warehouse.pk)}'
                           '&fields[TAX_VALUE]=0.0'
                           f'&fields[UF_CRM_1650617036]={SHIPPING_COMPANY}'
                           f'&fields[COMMENTS]={comments}')
                if code_B24_B24:
                    rq_text += f'&fields[COMPANY_ID]={code_B24_B24}'
                    outlet = Outlet.objects.get(pk=customer.id)
                    outlet.code_B24 = code_B24_B24
                    outlet.save()
                # f'&fields[BEGINDATE]={str(.creationDate).replace(" ", "T")}'
                # f'&fields[CLOSEDATE]={str(.deliveryDate).replace(" ", "T")}'
                #  '&fields[COMPANY_ID]=0&fields[CONTACT_ID]=0'
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
                    if i > 1:
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
                            result[order_no] = 'success'
                        else:
                            SendRequest.send_request_method(
                                f'{ENDPOINT_DEL_ORDER}?ID={order_code_B24}',
                                {}, portal=f'{PORTAL_B24}{TOKEN_B24}',
                                headers={},
                                http_method='get',
                            )
                            error_log = (f'Order No: {order_no}. Error send '
                                         'request B24 Order '
                                         'product. Status code: '
                                         f'`{status_code}`. {response.json()}')
                            SendRequest.logger.critical(error_log)
                            SendMessage.send_message(error_log)
                            raise SendRequestException(
                                f'Order No: {order_no}. {error_log}'
                            )
                    else:
                        SendRequest.send_request_method(
                            f'{ENDPOINT_DEL_ORDER}?ID={order_code_B24}',
                            {}, portal=f'{PORTAL_B24}{TOKEN_B24}',
                            headers={},
                            http_method='get',
                        )
                        raise SendRequestException(f'Order No: {order_no}. '
                                                   'No products in order')
                else:
                    error_log = (f'Order No: {order_no}. Error send request '
                                 'B24 Order. Status code: '
                                 f'`{status_code}`. {response.json()}')
                    SendRequest.logger.critical(error_log)
                    SendMessage.send_message(error_log)
                    raise SendRequestException(f'Order No: {order_no}. '
                                               f'{error_log}')
            else:
                raise SendRequestException(
                    f'Order No: {order_no}. Order code B24 <{order.code_B24}> '
                    'exist, but status not send'
                )
        return result
