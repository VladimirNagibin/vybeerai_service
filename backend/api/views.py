from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .exceptions import (NotFoundDataException, NotFoundEndpointException,
                         TokenReceivingException, SendRequestException)
from .send_requests import SendRequest
from .serializers import (CheckProductsSerializer, PriceListSerializer,
                          PricesSerializer, ProductStockSerializer,
                          StocksSerializer, UserTokenCreationSerializer)
from .services import create_orders, get_endpoint_data
from orders.models import PriceList
from warehouses.models import ProductStock


@api_view(('POST', ))
def send_request(request, way):
    """Вью для отправки запроса."""
    error = ''
    try:
        endpoint, data = get_endpoint_data(way)
        # status = 2 - change or insert / 9 - delete
    except NotFoundEndpointException as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
    except NotFoundDataException as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
    try:
        if way == 'orders':
            #response = SendRequest.send_request_token(endpoint, data,
            #                                          http_method='get')
            response = {
                "result": "",
                "countOrder": 3,
                "orders": [
                    {
                        "orderNo": "1",
                        "mainOrderNo": "1",
                        "outletExternalCode": "TT000000004",
                        "customerExternalCode": "1",
                        "payFormExternalCode": "000000039",
                        "orderTypeExternalCode": "1",
                        "deliveryDate": "13.11.2024 00:00:00",
                        "totalSum": 2400.00000,
                        "vatSum": 0.00000,
                        "discount": 0.00,
                        "creationDate": "12.11.2024 10:32:51",
                        "operationExternalCode": "2",
                        "warehouseExternalCode": "000000004",
                        "deliveryAddress": "г. Санкт-Петербург, ул. Якорная, 7 А",
                        "comment": "ТЕСТ",
                        "isReturn": False,
                        "olCardType": 4,
                        "outletData": None,
                        "details": [
                            {
                                "orderNo": "1",
                                "productExternalCode": "El000000507",
                                "price": 2400.00000,
                                "basePrice": 2400.00000,
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
                        "orderNo": "2",
                        "mainOrderNo": "2",
                        "outletExternalCode": "TT000000004",
                        "customerExternalCode": "1",
                        "payFormExternalCode": "000000039",
                        "orderTypeExternalCode": "1",
                        "deliveryDate": "13.11.2024 00:00:00",
                        "totalSum": 3300.00000,
                        "vatSum": 0.00000,
                        "discount": 0.00,
                        "creationDate": "12.11.2024 10:34:09",
                        "operationExternalCode": "1",
                        "warehouseExternalCode": "000000004",
                        "deliveryAddress": "г. Санкт-Петербург, ул. Якорная, 7 А",
                        "comment": "ТЕСТ",
                        "isReturn": False,
                        "olCardType": 4,
                        "outletData": None,
                        "details": [
                            {
                                "orderNo": "2",
                                "productExternalCode": "00000002033",
                                "price": 3300.00000,
                                "basePrice": 3300.00000,
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
                        "orderNo": "3",
                        "mainOrderNo": "3",
                        "outletExternalCode": "TT000000004",
                        "customerExternalCode": "1",
                        "payFormExternalCode": "000000039",
                        "orderTypeExternalCode": "1",
                        "deliveryDate": "13.11.2024 00:00:00",
                        "totalSum": 2900.00000,
                        "vatSum": 0.00000,
                        "discount": 0.00,
                        "creationDate": "12.11.2024 10:35:26",
                        "operationExternalCode": "3",
                        "warehouseExternalCode": "000000004",
                        "deliveryAddress": "г. Санкт-Петербург, ул. Якорная, 7 А",
                        "comment": "ТЕСТ ",
                        "isReturn": False,
                        "olCardType": 4,
                        "outletData": None,
                        "details": [
                            {
                                "orderNo": "3",
                                "productExternalCode": "El000001296",
                                "price": 2900.00000,
                                "basePrice": 2900.00000,
                                "qty": 1.00,
                                "vat": 0.00,
                                "discount": 0.00,
                                "isReturnable": 0,
                                "orderDPromo": []
                            }
                        ],
                        "orderHPromo": []
                    },
                ]
            }

            #create_orders(response)
            #SendRequest.send_orders_b24()
            send_request(request, 'syncOrders')
        else:
            response = SendRequest.send_request_token(endpoint, data)
        # processingType = 0 - all data / 1 - only for excange
        return Response(response, status=status.HTTP_200_OK)
    except TokenReceivingException as e:
        error = e
    except SendRequestException as e:
        error = e
    except Exception as e:
        error = e
    return Response(str(error), status=status.HTTP_400_BAD_REQUEST)


@api_view(('POST', ))
@permission_classes((AllowAny, ))
def get_token(request):
    """Вью для получение токена."""
    serializer = UserTokenCreationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    token = serializer.save()
    return Response(f'{token}', status=status.HTTP_200_OK)


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
