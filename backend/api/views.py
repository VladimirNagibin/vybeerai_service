import logging

from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .exceptions import (NotFoundDataException, NotFoundEndpointException,
                         TokenReceivingException, SendRequestException)
from .send_requests import SendRequest
from .serializers import (CheckProductsSerializer, OutletSlugSerializer,
                          PriceListSerializer, PricesSerializer,
                          ProductStockSerializer, StocksSerializer,
                          UserTokenCreationSerializer)
from .services import create_orders, get_endpoint_data
from orders.models import PriceList
from warehouses.models import Outlet, ProductStock, TypeStatusCompany

logger = logging.getLogger(__name__)


@api_view(('POST', ))
def send_request(request, way):
    """Вью для отправки запроса."""
    try:
        endpoint, data = get_endpoint_data(way)
        # status = 2 - change or insert / 9 - delete
    except (NotFoundEndpointException, NotFoundDataException) as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
    try:
        if way == 'orders':
            #response = SendRequest.send_request_token(endpoint, data,
            #                                          http_method='get')
            response = {
                "result": "",
                "countOrder": 2,
                "orders": [
                    {
                        "orderNo": "5",
                        "mainOrderNo": "5",
                        "outletExternalCode": "TT000000004",
                        "customerExternalCode": "1",
                        "payFormExternalCode": "000000039",
                        "orderTypeExternalCode": "1",
                        "deliveryDate": "27.12.2024 00:00:00",
                        "totalSum": 7015.00000,
                        "vatSum": 0.00000,
                        "discount": 0.00,
                        "creationDate": "19.12.2024 12:41:26",
                        "operationExternalCode": "3",
                        "warehouseExternalCode": "000000004",
                        "deliveryAddress": "Санкт-Петербург г., Среднеохтинский просп., 52/11А",
                        "comment": "ТЕСТ",
                        "isReturn": False,
                        "olCardType": 4,
                        "outletData": {
                            "orderNo": "5",
                            "tempOutletCode": "potential_92_271807",
                            "inn": "7802782309",
                            "legalName": "Шаг ООО",
                            "deliveryAddress": "Санкт-Петербург г., Среднеохтинский просп., 52/11А",
                            "phone": "+7 (999) 999-99-99",
                            "contactPerson": "ТЕСТ ТЕСТ"
                        },
                        "details": [
                            {
                                "orderNo": "5",
                                "productExternalCode": "00-00000110",
                                "price": 6490.00000,
                                "basePrice": 6490.00000,
                                "qty": 1.00,
                                "vat": 0.00,
                                "discount": 0.00,
                                "isReturnable": 0,
                                "orderDPromo": []
                            },
                            {
                                "orderNo": "5",
                                "productExternalCode": "00000001243",
                                "price": 525.00000,
                                "basePrice": 525.00000,
                                "qty": 1.00,
                                "vat": 0.00,
                                "discount": 0.00,
                                "isReturnable": 0,
                                "orderDPromo": []
                            }
                        ],
                        "orderHPromo": []
                    },
                    {
                        "orderNo": "6",
                        "mainOrderNo": "6",
                        "outletExternalCode": "TT000000004",
                        "customerExternalCode": "1",
                        "payFormExternalCode": "000000039",
                        "orderTypeExternalCode": "1",
                        "deliveryDate": "27.12.2024 00:00:00",
                        "totalSum": 4634.00000,
                        "vatSum": 0.00000,
                        "discount": 0.00,
                        "creationDate": "19.12.2024 12:43:38",
                        "operationExternalCode": "3",
                        "warehouseExternalCode": "000000004",
                        "deliveryAddress": "Санкт-Петербург г., Среднеохтинский просп., 1/1",
                        "comment": "ТЕСТ",
                        "isReturn": False,
                        "olCardType": 4,
                        "outletData": {
                            "orderNo": "6",
                            "tempOutletCode": "potential_92_374146",
                            "inn": "131656241155",
                            "legalName": "Светлакова О.А. ИП",
                            "deliveryAddress": "Санкт-Петербург г., Среднеохтинский просп., 1/1",
                            "phone": "+7 (888) 888-88-88",
                            "contactPerson": "ТЕСТ ТЕСТ"
                        },
                        "details": [
                            {
                                "orderNo": "6",
                                "productExternalCode": "El000000743",
                                "price": 1751.00000,
                                "basePrice": 1751.00000,
                                "qty": 1.00,
                                "vat": 0.00,
                                "discount": 0.00,
                                "isReturnable": 0,
                                "orderDPromo": []
                            },
                            {
                                "orderNo": "6",
                                "productExternalCode": "Bi000003478",
                                "price": 2883.00000,
                                "basePrice": 2883.00000,
                                "qty": 1.00,
                                "vat": 0.00,
                                "discount": 0.00,
                                "isReturnable": 0,
                                "orderDPromo": []
                            }
                        ],
                        "orderHPromo": []
                    }
                ]
            }

            if response['countOrder'] > 0:
                result = create_orders(response)
                if result:
                    response['result'] = result
                    return Response(
                        response, status=status.HTTP_400_BAD_REQUEST
                    )
        elif way == 'send_orders_b24':
            response = SendRequest.send_orders_b24()
        elif way == 'set_real_code':
            result = {}
            for dat in data:
                respon = SendRequest.send_request_token(endpoint, dat)
                result[dat['realExternalCode']] = respon
            response = result
        elif way == 'del_real_code':
            result = {}
            for dat in data:
                respon = SendRequest.send_request_token(endpoint, dat)
                result[dat['externalCode']] = respon
            response = result
        else:
            response = SendRequest.send_request_token(endpoint, data)
        # processingType = 0 - all data / 1 - only for excange
        return Response(response, status=status.HTTP_200_OK)
    except (TokenReceivingException, SendRequestException, Exception) as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


@api_view(('POST', ))
@permission_classes((AllowAny, ))
def get_token(request):
    """Вью для получение токена."""
    serializer = UserTokenCreationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    token = serializer.save()
    return Response(f'{token}', status=status.HTTP_200_OK)


@api_view(('GET', ))
def get_outlet_not_complit(request):
    """Вью для получение тт у которых не отправлены данные в выбирай."""
    outlets = Outlet.objects.filter(status=TypeStatusCompany.CONFIRMED)
    serializer = OutletSlugSerializer(outlets, many=True)
    return Response(serializer.data)


@api_view(('POST', ))
def set_outlet_not_complit(request):
    """Вью для установки в тт статуса выгружен в выбирай."""
    serializer = OutletSlugSerializer(data=request.data, many=True)
    serializer.is_valid(raise_exception=True)
    for data in serializer.data:
        Outlet.objects.filter(
            outletExternalCode=data['outletExternalCode']
        ).update(status=TypeStatusCompany.COMPLIT)
    return Response(serializer.data)


class ProductStockViewSet(viewsets.ModelViewSet):
    queryset = ProductStock.objects.all()
    serializer_class = ProductStockSerializer

    @action(
        detail=False,
        methods=('POST',),
        url_name='check_product',
        url_path=r'check_product',
    )
    def check_product(self, request, **kwargs):
        """Функция для проверки загруженных товаров."""
        serializer = CheckProductsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


    @action(
        detail=False,
        methods=('POST',),
        url_name='stocks',
        url_path=r'stocks',
    )
    def stocks(self, request, **kwargs):
        """Функция для загрузки остатков."""
        serializer = StocksSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class PriceListViewSet(viewsets.ModelViewSet):
    queryset = PriceList.objects.all()
    serializer_class = PriceListSerializer

    @action(
        detail=False,
        methods=('POST',),
        url_name='prices',
        url_path=r'prices',
    )
    def stocks(self, request, **kwargs):
        """Функция для загрузки цен."""
        serializer = PricesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
