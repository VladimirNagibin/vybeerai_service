from django.contrib import admin

from .models import (Company, Denial, Operation, OperationOutlet, Order,
                     OrderDetail, OrderHDenial, OrderInvoice, OutletData,
                     PayForm, PriceList, SalOutDetail)


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


class OrderDetailInline(admin.TabularInline):
    model = OrderDetail
    extra = 0


class OutletDataInline(admin.TabularInline):
    model = OutletData
    extra = 0


class OrderHDenialInline(admin.TabularInline):
    model = OrderHDenial
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (OutletDataInline, OrderDetailInline, OrderHDenialInline)
    list_display = (
        'orderNo',
        'mainOrderNo',
        'status',
        'warehouse',
        'payForm',
        'deliveryDate',
        'totalSum',
        'vatSum',
        'discount',
        'creationDate',
        'operation',
        'deliveryAddress',
        'comment',
    )
    list_editable = ('status',)
    search_fields = ('orderNo', 'warehouse')
    list_filter = ('status', 'orderNo', 'warehouse')


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('inn', 'legalName', 'code_B24')


@admin.register(Denial)
class DenialAdmin(admin.ModelAdmin):
    list_display = ('denialExternalCode', 'name', 'denialCode')
    list_editable = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(OrderHDenial)
class OrderHDenialAdmin(admin.ModelAdmin):
    list_display = ('order', 'denial')
    list_editable = ('denial',)
    search_fields = ('denial',)
    list_filter = ('denial',)


class SalOutDetailInline(admin.TabularInline):
    model = SalOutDetail
    extra = 0


@admin.register(OrderInvoice)
class OrderInvoiceAdmin(admin.ModelAdmin):
    inlines = (SalOutDetailInline, )
    list_display = (
        'order',
        'date',
        'invoiceExternalCode',
        'invoiceNo',
        'warehouse',
        'totalSum',
        'vatSum',
    )
    # list_editable = ('price',)
    search_fields = ('invoiceNo', 'warehouse')
    list_filter = ('invoiceNo', 'warehouse')


@admin.register(OperationOutlet)
class OperationOutletAdmin(admin.ModelAdmin):
    list_display = ('operation', 'outlet')
    #list_editable = ('denial',)
    #search_fields = ('denial',)
    #list_filter = ('denial',)
