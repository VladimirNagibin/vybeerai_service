from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import ProductStockViewSet, get_token

router_v1 = DefaultRouter()
router_v1.register(
    r'product_stock',
    ProductStockViewSet,
    basename='product_stock'
)

urlpatterns = [
    path('login/', get_token, name='token'),
    path('', include(router_v1.urls)),
]
