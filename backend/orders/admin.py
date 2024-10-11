from django.contrib import admin

from .models import Operation, PayForm, PriceList


# class AttributInline(admin.TabularInline):
#    model = ProductAttributValue
#    extra = 0


# class ImageInline(admin.TabularInline):
#    model = ProductImages
#    extra = 0


@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = (
        'operationExternalCode',
        'operationName',
        'coefficient',
    )
    list_editable = ('coefficient',)
    search_fields = ('operationName',)
    list_filter = ('operationName',)


@admin.register(PayForm)
class PayFormAdmin(admin.ModelAdmin):
    list_display = (
        'payFormExternalCode',
        'payFormName',
        'vatCalculationMode',
        'orderTypeExternalCode',
    )


@admin.register(PriceList)
class PriceListAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'payForm',
        'warehouse',
        'price',
        'vat',
        'productType',
    )
    list_editable = ('price',)
    search_fields = ('product',)
    list_filter = ('product',)
