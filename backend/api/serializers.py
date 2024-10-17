from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework_simplejwt.tokens import AccessToken

from products.models import Product
from warehouses.models import ProductStock, Warehouse

User = get_user_model()


class UserTokenCreationSerializer(serializers.Serializer):
    """Сериализатор для получения токена пользователем."""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def create(self, validated_data):
        user = get_object_or_404(User, username=self.data.get('username'))
        if not user.check_password(validated_data.get('password')):
            raise serializers.ValidationError('Неверное имя или пароль')
        return str(AccessToken.for_user(user))


class ProductStockSerializer(serializers.ModelSerializer):
    warehouse = SlugRelatedField(
        queryset=Warehouse.objects.all(),
        slug_field='warehouseExternalCode'
    )
    product = SlugRelatedField(
        queryset=Product.objects.all(),
        slug_field='productExternalCode'
    )

    class Meta:
        model = ProductStock
        fields = ('warehouse', 'product', 'stock')


class StocksSerializer(serializers.Serializer):
    """Сериалайзер для загрузки остатков"""
    stocks = ProductStockSerializer(many=True)

    class Meta:
        fields = ('stocks', )

    def create(self, validated_data):
        result = []
        for stock in validated_data['stocks']:
            product_stock = ProductStock.objects.get_or_create(
                warehouse=stock['warehouse'],
                product=stock['product'],
            )[0]
            product_stock.stock = stock['stock']
            product_stock.save()
            result.append(product_stock)
        return {"stocks": result}
