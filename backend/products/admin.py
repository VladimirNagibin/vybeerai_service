from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

from orders.models import PriceList
from .models import (Attribut, AttributValue, GroupProduct, Package,
                     Pictograph, Product, ProductAttributValue, ProductImages)
from warehouses.models import ProductStock

admin.site.unregister(Group)


class AttributInline(admin.TabularInline):
    model = ProductAttributValue
    extra = 0


class ImageInline(admin.TabularInline):
    model = ProductImages
    extra = 0


class PriceListInline(admin.TabularInline):
    model = PriceList
    extra = 0


class ProductStockInline(admin.TabularInline):
    model = ProductStock
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = (AttributInline, ImageInline, ProductStockInline,
               PriceListInline)
    list_display = (
        'productExternalCode',
        'productExternalName',
        'productName',
        'volume',
        'active',
        'description',
        'group',
        'codeBitrix',
        'package',
    )
    list_editable = ('productName', 'active', 'volume', 'description')
    search_fields = ('productExternalCode','productName', 'description',
                     'productExternalName')
    list_filter = ('group', 'active', 'package')


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('id', 'packageName', 'package_code')
    list_editable = ('packageName', 'package_code')
    search_fields = ('packageName',)


@admin.register(Pictograph)
class PictographAdmin(admin.ModelAdmin):
    list_display = ('pictograph', 'pictographName',)
    list_editable = ('pictographName',)
    search_fields = ('pictographName',)


class AttributValueInline(admin.TabularInline):
    model = AttributValue
    extra = 0


@admin.register(Attribut)
class AttributAdmin(admin.ModelAdmin):
    inlines = (AttributValueInline,)
    list_display = ('attributsName', 'attributsNameSortOrder', 'isFilter',
                    'isCardDetailsProduct')
    list_editable = ('attributsNameSortOrder', 'isFilter',
                     'isCardDetailsProduct')
    search_fields = ('attributsName',)
    list_filter = ('attributsName',)


@admin.register(AttributValue)
class AttributValueAdmin(admin.ModelAdmin):
    list_display = ('attribut', 'attributsValue', 'attributsValueSortOrder')
    list_editable = ('attributsValue', 'attributsValueSortOrder')
    search_fields = ('attribut',)
    list_filter = ('attribut',)


@admin.register(ProductImages)
class ProductImagesAdmin(admin.ModelAdmin):
    list_display = ('product', 'image_of_product', 'image',)
    # list_editable = ('pictographName',)
    search_fields = ('product',)
    list_filter = ('product',)

    @admin.display(description='Изображение')
    def image_of_product(self, obj):
        if obj.image:
            return mark_safe(
                f'<img src={obj.image.url} width="80" height="60">'
            )


@admin.register(GroupProduct)
class GroupProductAdmin(admin.ModelAdmin):
    list_display = ('name',)
    #list_editable = ('attributsValue', 'attributsValueSortOrder')
    search_fields = ('name',)
    #list_filter = ('name',)
