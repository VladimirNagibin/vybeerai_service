from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import get_token

urlpatterns = [
    path('login/', get_token, name='token'),
]
