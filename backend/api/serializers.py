import logging

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework_simplejwt.tokens import AccessToken

from orders.models import (Operation, Order, OrderDetail,
                           PayForm, PriceList)
from products.models import GroupProduct, Package, Pictograph, Product
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
    codeBitrix = serializers.CharField()
    group = SlugRelatedField(
        queryset=GroupProduct.objects.all(),
        slug_field='name'
    )

    class Meta:
        fields = ('productExternalCode', 'productExternalName', 'package',
                  'codeBitrix', 'group')


class CheckProductsSerializer(serializers.Serializer):
    """Сериалайзер для проверки товаров."""

    check_products = CheckProductSerializer(many=True)

    class Meta:
        fields = ('check_products',)

    def create(self, validated_data):
        result = []
        product_update = []
        product_active = {
            product for product in Product.objects.filter(active=True)
        }
        for check_product in validated_data['check_products']:
            #logger = logging.getLogger(__name__)
            #logger.debug(f'{type(check_product["group"])}===============')
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
                        codeBitrix=check_product['codeBitrix'],
                        volume=0,
                        package=check_product['package'],
                        description='-----',
                        pictograph=Pictograph.objects.get(pk=7),
                        active=False,
                        group=check_product['group'],
                    )
                )
            else:
            #    cur_product = current_product[0]
                #logger.debug(f'{type(check_product["group"])}===============')
                product_active.discard(current_product[0])
                current_product.update(group=check_product.get('group'),
                                       productExternalName=product_name,
                                       codeBitrix=check_product['codeBitrix'])
            #    if not 
            #    cur_product.productExternalName = product_name
            #    cur_product.codeBitrix = check_product['codeBitrix']
            #    cur_product.group = check_product.get('group'),
                #cur_product.group = GroupProduct.objects.get(pk=1),
            #    product_update.append(cur_product)
        if product_active:
            for product in product_active:
                product.active = False
                product.save()
        if result:
            Product.objects.bulk_create(result)
        #if product_update:
        #    Product.objects.bulk_update(product_update,)
        #                                #['productExternalName', 'codeBitrix', 'group'])
        return {"check_products": result}


class PriceListSerializer(serializers.ModelSerializer):
    payForm = SlugRelatedField(
        queryset=PayForm.objects.all(),
        slug_field='payFormExternalCode',
        default=PayForm.objects.get(pk=1),
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
                payForm=price['payForm'],
            )[0]
            price_list.price = price['price']
            price_list.save()
            result.append(price_list)
        return {"prices": result}

    def validate(self, data):
        #prices_warehouse = []
        warehouse = Warehouse.objects.get(pk=1)
        for price in data['prices']:
            if 'warehouse' not in price:
                price['warehouse'] = warehouse
                #for warehouse in Warehouse.objects.all():
                #    price_warehouse = price.copy()
                #    price_warehouse['warehouse'] = warehouse
                #    prices_warehouse.append(price_warehouse)
            #else:
                #prices_warehouse.append(price.copy())
        #return {'prices': prices_warehouse}
        return data


class OrderSerializer(serializers.ModelSerializer):

    warehouseExternalCode = serializers.SlugRelatedField(
        queryset=Warehouse.objects.all(),
        slug_field='warehouseExternalCode',
        source='warehouse'
    )
    payFormExternalCode = serializers.SlugRelatedField(
        queryset=PayForm.objects.all(),
        slug_field='payFormExternalCode',
        source='payForm'
    )
    operationExternalCode = serializers.SlugRelatedField(
        queryset=Operation.objects.all(),
        slug_field='operationExternalCode',
        source='operation'
    )
    creationDate = serializers.CharField()
    deliveryDate = serializers.CharField()

    class Meta:
        model = Order
        fields = ('orderNo', 'mainOrderNo', 'warehouseExternalCode',
                  'payFormExternalCode', 'orderTypeExternalCode',
                  'deliveryDate', 'totalSum', 'vatSum', 'discount',
                  'creationDate', 'operationExternalCode', 'deliveryAddress',
                  'comment', 'isReturn', 'olCardType')

    @staticmethod
    def update_format_date(value):
        value_tmp = value.split()
        date_tmp = value_tmp[0].split('.')
        return f'{date_tmp[2]}-{date_tmp[1]}-{date_tmp[0]}T{value_tmp[1]}'

    def validate_creationDate(self, value):
        return self.update_format_date(value)

    def validate_deliveryDate(self, value):
        return self.update_format_date(value)


class OrderDetailSerializer(serializers.ModelSerializer):

    orderNo = serializers.SlugRelatedField(
        queryset=Order.objects.all(),
        slug_field='orderNo',
        source='order'
    )
    productExternalCode = serializers.SlugRelatedField(
        queryset=Product.objects.all(),
        slug_field='productExternalCode',
        source='product'
    )

    class Meta:
        model = OrderDetail
        fields = ('orderNo', 'productExternalCode', 'price', 'basePrice',
                  'qty', 'vat', 'discount')


#class CompanySerializer(serializers.ModelSerializer):

#    class Meta:
#        model = Company
#        fields = ('inn', 'legalName', 'tempOutletCode')


#class OutletDataSerializer(serializers.ModelSerializer):

#    orderNo = serializers.SlugRelatedField(
#        queryset=Order.objects.all(),
#        slug_field='orderNo',
#        source='order'
#    )

#    class Meta:
#        model = OutletData
#        fields = ('orderNo', 'tempOutletCode', 'company', 'deliveryAddress',
#                  'phone', 'contactPerson')
