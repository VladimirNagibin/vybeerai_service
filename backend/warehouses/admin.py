from django.contrib import admin

from .models import Outlet, ProductStock, Warehouse
from orders.models import DeliveryDate, OperationOutlet, OutletPayForm


class OperationOutletInline(admin.TabularInline):
    model = OperationOutlet
    extra = 0


class DeliveryDateInline(admin.TabularInline):
    model = DeliveryDate
    extra = 0


class PayFormInline(admin.TabularInline):
    model = OutletPayForm
    extra = 0


@admin.register(Outlet)
class OutletAdmin(admin.ModelAdmin):
    inlines = (DeliveryDateInline, PayFormInline, OperationOutletInline)
    list_display = ('outletExternalCode', 'outletName', 'warehouse')
    list_editable = ('outletName',)
    search_fields = ('outletName',)
    list_filter = ('outletName',)


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('warehouseExternalCode', 'customerExternalCode',
                    'warehouseName', 'allowTareReturn')
    list_editable = ('warehouseName',)
    search_fields = ('warehouseName',)
    list_filter = ('warehouseName',)


@admin.register(ProductStock)
class ProductStockAdmin(admin.ModelAdmin):
    list_display = ('warehouse', 'product', 'stock')
    list_editable = ('stock',)
    search_fields = ('warehouse', 'product')
    list_filter = ('warehouse', 'product')
