import logging
import os

from dotenv import load_dotenv

from .exceptions import NotFoundDataException, NotFoundEndpointException
from .serializers import (CompanySerializer, OrderDetailSerializer,
                          OrderSerializer, OutletDataSerializer)
from orders.models import (Company, DeliveryDate, OperationOutlet, Order,
                           OrderDetail, OutletData, OutletPayForm, PayForm,
                           PriceList, TypeStatusCompany, TypeStatusOrders)
from products.models import Product, ProductAttributValue
from warehouses.models import Outlet, ProductStock, Warehouse

load_dotenv()

SUPPLIER_ID = os.getenv('SUPPLIER_ID')


STATUS_CHANGE_OR_UPDATE = 2


ENDPOINTS = {
    'productWarehouses': '/Warehouse/productWarehouses',
    'loadProduct': '/Product/loadProduct/',
    'loadProductAttributs': '/Product/loadProductAttributs/',
    'productStocks': '/Warehouse/productStocks/',
    'outletWarehouses': '/Warehouse/outletWarehouses/',
    'operations': '/Order/operations/',
    'deliveryDates': '/Order/deliveryDates/',
    'payForms': '/PayForm/payForms/',
    'outletPayForms': '/PayForm/outletPayForms/',
    'priceLists': '/PayForm/priceLists/',
    'orders': f'/SyncOrder/orders/{SUPPLIER_ID}',
    'syncOrders': '/SyncOrder/syncOrders',
    'send_orders_b24': '/send_orders_b24',
    'set_real_code': '/set-real-external-code',
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
        for outlet in Outlet.objects.all():
            data.append({
                'outletExternalCode': outlet.outletExternalCode,
                'warehouseExternalCode': outlet.warehouse
                .warehouseExternalCode,
                'customerExternalCode': outlet.warehouse.customerExternalCode,
                'status': status,
            })
    elif way == 'operations':
        for operation in OperationOutlet.objects.all():
            data.append({
                'outletExternalCode': operation
                .outlet
                .outletExternalCode,
                'operationExternalCode': operation
                .operation
                .operationExternalCode,
                'operationName': operation
                .operation
                .operationName,
                'customerExternalCode': operation
                .outlet
                .warehouse
                .customerExternalCode,
                'coefficient': operation
                .operation
                .coefficient,
                'status': status,
            })
    elif way == 'deliveryDates':
        for delivery_date in DeliveryDate.objects.all():
            for deliv_date in delivery_date.deliveryDate.split(', '):
                data.append({
                    'outletExternalCode': delivery_date
                    .outlet
                    .outletExternalCode,
                    'customerExternalCode': delivery_date
                    .outlet
                    .warehouse
                    .customerExternalCode,
                    'deliveryDate': deliv_date,
                    'deadLine': delivery_date.deadLine,
                    'minSum': delivery_date.minSum,
                    'status': status,
                })
    elif way == 'outletPayForms':
        for pay_forms in OutletPayForm.objects.all():
            data.append({
                'outletExternalCode': pay_forms
                .outlet
                .outletExternalCode,
                'payFormExternalCode': pay_forms.payForm.payFormExternalCode,
                'customerExternalCode': pay_forms
                .outlet
                .warehouse
                .customerExternalCode,
                'status': status,
            })
    elif way == 'payForms':
        for pay_form in PayForm.objects.all():
            data.append({
                'payFormExternalCode': pay_form.payFormExternalCode,
                'payFormName': pay_form.payFormName,
                'vatCalculationMode': (1
                                       if pay_form.vatCalculationMode
                                       else 0),
                'customerExternalCode': '1',
                'orderTypeExternalCode': pay_form.orderTypeExternalCode,
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
    elif way == 'orders':
        return data
    elif way == 'send_orders_b24':
        return data
    elif way == 'syncOrders':
        orders = Order.objects.filter(status=TypeStatusOrders.SEND_B24)
        for order in orders:
            data.append({'orderNo': order.orderNo})
    elif way == 'set_real_code':
        companies = Company.objects.filter(
            status=TypeStatusCompany.CODE_RECEIVED
        )
        for company in companies:
            data.append({'potentialExternalCode': company.tempOutletCode,
                         'realExternalCode': company.realExternalCode})
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


def create_orders(data):
    orders = data['orders']
    for order in orders:
        order_no = order['orderNo']
        order_doc = Order.objects.filter(orderNo=order_no)
        if order_doc:
            ser_order = OrderSerializer(order_doc[0], data=order)
        else:
            ser_order = OrderSerializer(data=order)
        ser_order.is_valid(raise_exception=True)
        order_instance = ser_order.save()
        products = order['details']
        for product in products:
            order_no = product['orderNo']
            product_no = product['productExternalCode']
            product_doc = OrderDetail.objects.filter(
                order=Order.objects.get(orderNo=order_no),
                product=Product.objects.get(productExternalCode=product_no)
            )
            if product_doc:
                ser_product = OrderDetailSerializer(product_doc[0],
                                                    data=product)
            else:
                ser_product = OrderDetailSerializer(data=product)
            ser_product.is_valid(raise_exception=True)
            ser_product.save()
        outlet_data = order.get('outletData')
        if outlet_data:
            order_no = outlet_data['orderNo']
            temp_outlet_code = outlet_data['tempOutletCode']
            inn = outlet_data['inn']
            legal_name = outlet_data.get('legalName')
            delivery_address = outlet_data.get('deliveryAddress')
            phone = outlet_data['phone']
            contact_person = outlet_data.get('contactPerson')
            company_doc = Company.objects.filter(inn=inn)
            data_company = {'inn': inn,
                            'legalName': legal_name if legal_name else '',
                            'tempOutletCode': temp_outlet_code}
            print(data_company)
            if company_doc:
                ser_company = CompanySerializer(company_doc[0],
                                                data=data_company)
            else:
                ser_company = CompanySerializer(data=data_company)
            ser_company.is_valid(raise_exception=True)
            company = ser_company.save()
            outlet_data_doc = OutletData.objects.filter(order=order_instance)
            data_outlet_data = {'orderNo': order_no,
                                'tempOutletCode': temp_outlet_code,
                                'company': company.pk,
                                'deliveryAddress':
                                delivery_address if delivery_address else '',
                                'phone': phone,
                                'contactPerson':
                                contact_person if contact_person else ''}
            if outlet_data_doc:
                ser_outlet_data = OutletDataSerializer(outlet_data_doc[0],
                                                       data=data_outlet_data)
            else:
                ser_outlet_data = OutletDataSerializer(data=data_outlet_data)
            ser_outlet_data.is_valid(raise_exception=True)
            ser_outlet_data.save()
