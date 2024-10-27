from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (PriceListViewSet, ProductStockViewSet, get_token,
                       send_request)

router_v1 = DefaultRouter()
router_v1.register(
    r'product_stock',
    ProductStockViewSet,
    basename='product_stock'
)
router_v1.register(
    r'price_list',
    PriceListViewSet,
    basename='price_list'
)

urlpatterns = [
    path('login/', get_token, name='token'),
    path('send/<slug:way>/', send_request, name='send_request'),
    path('', include(router_v1.urls)),
]
