from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
# from django.utils.safestring import mark_safe

from .models import Product, ProductAttribut, ProductImages


class AttributInline(admin.TabularInline):
    model = ProductAttribut
    extra = 0


class ImageInline(admin.TabularInline):
    model = ProductImages
    extra = 0


@admin.register(Product)
class CategoryAdmin(admin.ModelAdmin):
    inlines = (AttributInline, ImageInline)
    list_display = (
        'productExternalCode',
        'productExternalName',
        'productName',
    )
    list_editable = ('productName',)
    search_fields = ('productName', 'description')
    list_filter = ('productName',)
