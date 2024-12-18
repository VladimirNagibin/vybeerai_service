from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (PriceListViewSet, ProductStockViewSet, get_token,
                       get_outlet_not_complit, send_request,
                       set_outlet_not_complit)

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
    path(
        'outlet_not_complit/',
        get_outlet_not_complit,
        name='outlet_not_complit',
    ),
    path(
        'outlet_set_complit/',
        set_outlet_not_complit,
        name='outlet_set_complit',
    ),
    path('send/<slug:way>/', send_request, name='send_request'),
    path('', include(router_v1.urls)),
]
