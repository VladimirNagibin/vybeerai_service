from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework_simplejwt.tokens import AccessToken

from orders.models import PayForm, PriceList
from products.models import Package, Pictograph,Product
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
    """Сериалайзер для загрузки остатков."""

    stocks = ProductStockSerializer(many=True)

    class Meta:
        fields = ('stocks',)

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


class CheckProductSerializer(serializers.Serializer):
    """Сериалайзер для проверки товара."""

    productExternalCode = serializers.CharField()
    productExternalName = serializers.CharField()
    package = SlugRelatedField(
        queryset=Package.objects.all(),
        slug_field='packageName'
    )

    class Meta:
        fields = ('productExternalCode', 'productExternalName', 'package')


class CheckProductsSerializer(serializers.Serializer):
    """Сериалайзер для проверки товаров."""

    check_products = CheckProductSerializer(many=True)

    class Meta:
        fields = ('check_products',)

    def create(self, validated_data):
        result = []
        product_active = {
            product for product in Product.objects.filter(active=True)
        }
        for check_product in validated_data['check_products']:
            product_code, product_name = (check_product['productExternalCode'],
                                          check_product['productExternalName'])
            current_product = Product.objects.filter(
                productExternalCode=product_code
            )
            if not current_product:
                result.append(
                    Product(
                        productExternalCode=product_code,
                        productExternalName=product_name,
                        productName=product_name,
                        volume=0,
                        package=check_product['package'],
                        description='-----',
                        pictograph=Pictograph.objects.get(pk=7),
                        active=False,
                    )
                )
            else:
                product_active.discard(current_product[0])
        if product_active:
            for product in product_active:
                product.active = False
                product.save()
        if result:
            Product.objects.bulk_create(result)
        return {"check_products": result}


class PriceListSerializer(serializers.ModelSerializer):
    payForm = SlugRelatedField(
        queryset=PayForm.objects.all(),
        slug_field='payFormExternalCode',
        default='1',
    )
    warehouse = SlugRelatedField(
        queryset=Warehouse.objects.all(),
        slug_field='warehouseExternalCode',
        required=False,
    )
    product = SlugRelatedField(
        queryset=Product.objects.all(),
        slug_field='productExternalCode',
    )

    class Meta:
        model = PriceList
        fields = ('payForm', 'warehouse', 'product', 'price')


class PricesSerializer(serializers.Serializer):
    """Сериалайзер для загрузки цен"""

    prices = PriceListSerializer(many=True)

    class Meta:
        fields = ('prices',)

    def create(self, validated_data):
        result = []
        for price in validated_data['prices']:
            price_list = PriceList.objects.get_or_create(
                warehouse=price['warehouse'],
                product=price['product'],
            )[0]
            price_list.price = price['price']
            price_list.save()
            result.append(price_list)
        return {"prices": result}

    def validate(self, data):
        prices_warehouse = []
        for price in data['prices']:
            if 'warehouse' not in price:
                for warehouse in Warehouse.objects.all():
                    price_warehouse = price.copy()
                    price_warehouse['warehouse'] = warehouse
                    prices_warehouse.append(price_warehouse)
            else:
                prices_warehouse.append(price.copy())
        return {'prices': prices_warehouse}
