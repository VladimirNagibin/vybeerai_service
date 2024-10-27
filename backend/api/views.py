from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .exceptions import TokenReceivingException, SendRequestException
from .send_requests import SendRequest
from .serializers import (PriceListSerializer, PricesSerializer,
                          ProductStockSerializer, StocksSerializer,
                          UserTokenCreationSerializer)
from .services import get_endpoint_data
from orders.models import PriceList
from warehouses.models import ProductStock


@api_view(('POST', ))
@permission_classes((AllowAny, ))
def send_request(request, way):
    """Вью для отправки запроса."""
    endpoint, data = get_endpoint_data(way)
    error = ''
    try:
        response = SendRequest.send_request_token(endpoint, data)
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
        """Функция для загрузки остатков."""
        serializer = PricesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
