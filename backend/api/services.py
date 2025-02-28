import logging
import os

from django.db.models import Q
from dotenv import load_dotenv
from rest_framework.exceptions import ValidationError

from .exceptions import NotFoundDataException, NotFoundEndpointException
from .serializers import (OrderDetailSerializer, OrderSerializer)
from orders.models import (DeliveryDate, Operation, OperationOutlet, Order,
                           OrderDetail, Outlet, OutletPayForm, PayForm,
                           PriceList, TypeStatusOrders)
from products.models import Product, ProductAttributValue
from warehouses.models import (Outlet, ProductStock, TypeStatusCompany,
                               Warehouse)

load_dotenv()

SUPPLIER_ID = os.getenv('SUPPLIER_ID')

STATUS_CHANGE_OR_UPDATE = 2

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
    'orders': f'/SyncOrder/orders/{SUPPLIER_ID}',
    'syncOrders': '/SyncOrder/syncOrders',
    'send_orders_b24': '/send_orders_b24',
    'set_real_code': '/set-real-external-code',
    'del_real_code': '/close-outlet',
}

logger = logging.getLogger(__name__)

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
        for outlet in Outlet.objects.filter(
            Q(
                status=TypeStatusCompany.CONFIRMED
            ) | Q(status=TypeStatusCompany.COMPLIT)
        ):
            data.append({
                'outletExternalCode': outlet.outletExternalCode,
                'warehouseExternalCode': outlet.warehouse
                .warehouseExternalCode,
                'customerExternalCode': outlet.warehouse.customerExternalCode,
                'status': status,
            })
    elif way == 'operations':
        for operation in OperationOutlet.objects.filter(
            Q(
                outlet__status=TypeStatusCompany.CONFIRMED
            ) | Q(outlet__status=TypeStatusCompany.COMPLIT)
        ):
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
        for delivery_date in DeliveryDate.objects.filter(
            Q(
                outlet__status=TypeStatusCompany.CONFIRMED
            ) | Q(outlet__status=TypeStatusCompany.COMPLIT)
        ):
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
        for pay_forms in OutletPayForm.objects.filter(
            Q(
                outlet__status=TypeStatusCompany.CONFIRMED
            ) | Q(outlet__status=TypeStatusCompany.COMPLIT)
        ):
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
        return data    
    elif way == 'set_real_code':
        companies = Outlet.objects.filter(
            status=TypeStatusCompany.CODE_RECEIVED
        )
        for company in companies:
            data.append({'potentialExternalCode': company.tempOutletCode,
                         'realExternalCode': company.outletExternalCode})
        return data
    elif way == 'del_real_code':
        companies = Outlet.objects.filter(
            status=TypeStatusCompany.CANCEL
        )
        for company in companies:
            data.append({'externalCode': company.outletExternalCode})
        return data
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
    result = {}
    for order in orders:
        order_no = order['orderNo']
        order_doc = Order.objects.filter(orderNo=order_no)
        logger.info(f'{order_no}================')
        if order_doc:
            ser_order = OrderSerializer(
                order_doc[0],
                data=(order | {'status': TypeStatusOrders.RECEIVED})
            )
        else:
            ser_order = OrderSerializer(data=order)
        try:
            ser_order.is_valid(raise_exception=True)
        except ValidationError as e:
            logger.info(f'{e}================')
            result[order_no] = 'Exception created order'
            continue
        order_instance = ser_order.save()
        products = order['details']
        try:
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
        except (ValidationError, KeyError, Exception) as e:
            order_instance.status = TypeStatusOrders.NOT_COMPLIT
            order_instance.save()
            result[order_no] = f'Exception created products {e}'
            continue
        try:
            if outlet_data := order.get('outletData'):
                temp_outlet_code = outlet_data['tempOutletCode']
                legal_name = outlet_data.get('legalName', '')
                delivery_address = outlet_data.get('deliveryAddress', '')
                contact_person = outlet_data.get('contactPerson', '')
                inn = outlet_data['inn']
                outlets = Outlet.objects.filter(
                    Q(inn=inn) & Q(tempOutletCode=temp_outlet_code)
                )
                if outlets:
                    outlet = Outlet.objects.get(
                        inn=inn, tempOutletCode=temp_outlet_code
                    )
                else:
                    outlet = Outlet(
                        outletExternalCode=temp_outlet_code,
                        outletName=f'TT {legal_name}',
                        warehouse=Warehouse.objects.get(
                            warehouseExternalCode=order['warehouseExternalCode']
                        ),
                        inn=inn,
                        legalName=legal_name,
                        tempOutletCode=temp_outlet_code,
                        deliveryAddress=delivery_address,
                        phone=outlet_data['phone'],
                        contactPerson=contact_person,
                    )
                    outlet.save()
                if outlet.status == TypeStatusCompany.RECEIVED:
                    id = outlet.pk
                    outlet.outletExternalCode = f'TTVY00{id}'
                    outlet.status = TypeStatusCompany.CODE_RECEIVED
                    outlet.save()
                OperationOutlet.objects.get_or_create(
                    operation=Operation.objects.get(pk=3), outlet=outlet
                )
                DeliveryDate.objects.get_or_create(
                    outlet=outlet,
                    deliveryDate='Пн, Вт, Ср, Чт, Пт',
                    deadLine='19:00',
                    minSum=3000.0
                )
                OutletPayForm.objects.get_or_create(
                    outlet=outlet,
                    payForm=PayForm.objects.get(pk=1)
                )
                order_instance.outlet = outlet
                order_instance.save()
            else:
                try:
                    outlet = Outlet.objects.filter(
                        outletExternalCode=order['outletExternalCode']
                    )
                    if outlet:
                        order_instance.outlet = outlet[0]
                        order_instance.save()
                except Exception as e:
                    raise e
        except ValidationError:
            order_instance.status = TypeStatusOrders.NOT_COMPLIT
            order_instance.save()
            result[order_no] = 'Exception created outlet'
        except Exception as e:
            order_instance.status = TypeStatusOrders.NOT_COMPLIT
            order_instance.save()
            ex = 'Exception created outlet'
            result[order_no] = f'{ex}: {e}'
    return result
