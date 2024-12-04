from django.core.validators import MinValueValidator
from django.db import models

from core.constants import (COMMENT_MAX_LENGHT, NAME_EXT_MAX_LENGHT,
                            NAME_MAX_LENGHT, PRESENTATION_MAX_LENGTH)

from products.models import Product


class TypeStatusCompany(models.IntegerChoices):
    RECEIVED = 1, 'Получен'
    CODE_RECEIVED = 2, 'Получен код УС'
    CONFIRMED = 3, 'Отправлен код УС'


class Outlet(models.Model):
    outletExternalCode = models.CharField(
        'Внешний код ТТ',
        max_length=NAME_EXT_MAX_LENGHT,
        unique=True,
    )
    outletName = models.CharField(
        'Наименование ТТ в 1С',
        max_length=NAME_MAX_LENGHT,
        # unique=True,
        blank=True,
    )
    warehouse = models.ForeignKey(
        'Warehouse',
        on_delete=models.CASCADE,
        verbose_name='склад',
        related_name='outlets',
        null=True  # CHECKED !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    )
    inn = models.CharField(
        'ИНН',
        max_length=NAME_EXT_MAX_LENGHT,
        #unique=True,
        blank=True
    )
    legalName = models.CharField(
        'Юридическое название',
        max_length=COMMENT_MAX_LENGHT,
        blank=True,
    )
    code_B24 = models.PositiveIntegerField('Код Битрикс', #unique=True,
                                           null=True, default=None)
    tempOutletCode = models.CharField(
        'Временный внешний код ТТ',
        max_length=NAME_EXT_MAX_LENGHT,
        blank=True,
    )
    #realExternalCode = models.CharField(
    #    'Код в УС',
    #    max_length=NAME_EXT_MAX_LENGHT,
    #    blank=True,
    #)
    status = models.PositiveSmallIntegerField(
        'Статус',
        choices=TypeStatusCompany.choices,
        default=TypeStatusCompany.RECEIVED,
    )
    deliveryAddress = models.CharField(
        'Адрес доставки',
        max_length=COMMENT_MAX_LENGHT,
        blank=True,
    )
    phone = models.CharField(
        'Телефон',
        max_length=NAME_EXT_MAX_LENGHT,
        blank=True,
    )
    contactPerson = models.CharField(
        'Контактное лицо',
        max_length=COMMENT_MAX_LENGHT,
        blank=True,
    )

    # outletClassificationExternalCode
    # outletAddress
    # deliveryAddress
    # outletTradingName
    # olCode
    # geographyExternalCode
    # networkExternalCode
    # customerExternalCode
    # outletInn
    # juridicalName
    # olGroupName

    class Meta:
        ordering = ('outletName',)
        verbose_name = 'компания'
        verbose_name_plural = 'Компании'

    def __str__(self):
        return self.outletName[:PRESENTATION_MAX_LENGTH]


class Warehouse(models.Model):
    warehouseExternalCode = models.CharField(
        'Код склада в 1С',
        max_length=NAME_EXT_MAX_LENGHT,
        unique=True,
    )
    customerExternalCode = models.CharField(
        'Внешний код точки синхронизации',
        max_length=NAME_EXT_MAX_LENGHT,
        help_text=('Если точка синхронизации не используется, '
                   'равно warehouseExternalCode'),
        default='1',
    )
    warehouseName = models.CharField(
        'Наименование склада',
        max_length=NAME_EXT_MAX_LENGHT,
        unique=True,
    )
    allowTareReturn = models.BooleanField(
        'Признак возврата тары: 1-да, 0-нет',
        default=False,
        null=True,
        blank=True,
    )
    #outlet = models.OneToOneField(
    #    Outlet,
    #    on_delete=models.CASCADE,
    #    verbose_name='Торговая точка',
    #    related_name='warehouses',
    #)

    class Meta:
        ordering = ('warehouseName',)
        verbose_name = 'склад'
        verbose_name_plural = 'Склады'

    def __str__(self):
        return self.warehouseName[:PRESENTATION_MAX_LENGTH]


class ProductStock(models.Model):
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        verbose_name='склад',
        related_name='product_stocks',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='товар',
        related_name='product_stocks',
    )
    stock = models.FloatField(  # numeric(13, 3)
        'Остаток на складе',
        validators=[MinValueValidator(0.0)],
        default=0,
        help_text=('Необходимость передачи нулевого значения зависит от: '
                   'processingType = 0 – можно не передавать '
                   'processingType = 1 – нужно передавать')
    )

    class Meta:
        ordering = ('warehouse', 'product')
        verbose_name = 'остатки товаров на складах'
        verbose_name_plural = 'Остатки товаров на складах'
        constraints = (
            models.UniqueConstraint(
                fields=('warehouse', 'product'),
                name='unique_warehouse_product'
            ),
        )

    def __str__(self):
        return (f'{self.product} {self.warehouse} '
                f'{self.stock}')
