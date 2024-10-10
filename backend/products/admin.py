from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

from .models import (Attribut, AttributValue, Package, Pictograph, Product,
                     ProductAttributValue, ProductImages)


admin.site.unregister(Group)


class AttributInline(admin.TabularInline):
    model = ProductAttributValue
    extra = 0


class ImageInline(admin.TabularInline):
    model = ProductImages
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = (AttributInline, ImageInline)
    list_display = (
        'productExternalCode',
        'productExternalName',
        'productName',
    )
    list_editable = ('productName',)
    search_fields = ('productName', 'description')
    list_filter = ('productName',)


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('id', 'packageName',)
    list_editable = ('packageName',)
    search_fields = ('packageName',)
    list_filter = ('packageName',)


@admin.register(Pictograph)
class PictographAdmin(admin.ModelAdmin):
    list_display = ('pictograph', 'pictographName',)
    list_editable = ('pictographName',)
    search_fields = ('pictographName',)
    list_filter = ('pictographName',)


@admin.register(Attribut)
class AttributAdmin(admin.ModelAdmin):
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
