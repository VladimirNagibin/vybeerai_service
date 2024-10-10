from django.contrib import admin

from .models import Outlet, ProductStock, Warehouse


@admin.register(Outlet)
class OutletAdmin(admin.ModelAdmin):
    list_display = ('outletExternalCode', 'outletName',)
    list_editable = ('outletName',)
    search_fields = ('outletName',)
    list_filter = ('outletName',)


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('warehouseExternalCode', 'customerExternalCode',
                    'warehouseName', 'outlet', 'allowTareReturn')
    list_editable = ('warehouseName',)
    search_fields = ('warehouseName',)
    list_filter = ('warehouseName',)


@admin.register(ProductStock)
class ProductStockAdmin(admin.ModelAdmin):
    list_display = ('warehouse', 'product', 'stock')
    list_editable = ('stock',)
    search_fields = ('warehouse', 'product')
    list_filter = ('warehouse', 'product')
