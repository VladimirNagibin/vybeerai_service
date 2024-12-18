# from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from core.constants import (CODE_EXT_MAX_LENGHT, COMMENT_MAX_LENGHT,
                            DEAD_LINE_MAX_LENGHT, NAME_EXT_MAX_LENGHT,
                            NAME_MAX_LENGHT, PRESENTATION_MAX_LENGTH)
from products.models import Product
from warehouses.models import Outlet, Warehouse


class Operation(models.Model):
    """Наличный, Безналичный, По условиям договора."""

    operationExternalCode = models.CharField(
        'Внешний код Типа операции',
        max_length=NAME_EXT_MAX_LENGHT,
    )
    operationName = models.CharField(
        'Название Типа операции',
        max_length=NAME_EXT_MAX_LENGHT,
    )
    coefficient = models.FloatField(  # numeric(5,2)
        'Коэффициент ',
        validators=[MinValueValidator(0.0)],
        default=1.0,
        help_text=('Значение влияет на общую суму заказа (поле является '
                   'пользовательским). '
                   'Для нулевого влияния указывать значение “1”.')
    )

    class Meta:
        ordering = ('operationName',)
        verbose_name = 'операция'
        verbose_name_plural = 'Операции'

    def __str__(self):
        return self.operationName[:PRESENTATION_MAX_LENGTH]


class OperationOutlet(models.Model):
    operation = models.ForeignKey(
        Operation,
        on_delete=models.CASCADE,
        verbose_name='операция',
        related_name='operatin_outlets',
    )
    outlet = models.ForeignKey(
        Outlet,
        on_delete=models.CASCADE,
        verbose_name='ТТ',
        related_name='operations_outlet',
        null=True  # CHECKED !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    )

    class Meta:
        ordering = ('outlet', 'operation')
        verbose_name = 'операция по торговой точке'
        verbose_name_plural = 'Операции по торговым точкам'
        constraints = (
            models.UniqueConstraint(
                fields=('outlet', 'operation'),
                name='unique_outlet_operation'
            ),
        )

    def __str__(self):
        return f'{self.outlet} {self.operation}'


class DeliveryDate(models.Model):
    outlet = models.ForeignKey(
        Outlet,
        on_delete=models.CASCADE,
        verbose_name='ТТ',
        related_name='deliverydates_outlet',
        null=True  # CHECKED !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    )
    deliveryDate = models.CharField(
        'Дни доставки',
        max_length=NAME_EXT_MAX_LENGHT,
        default='Пн, Вт, Ср, Чт, Пт',
        null=True,
        blank=True,
    )
    deadLine = models.CharField(
        'Граничное времени обработки заказа',
        max_length=DEAD_LINE_MAX_LENGHT,
        default='17:00',
        null=True,
        blank=True,
    )
    minSum = models.FloatField(  # numeric(18,2)
        'Минимальная сумма заказа',
        validators=[MinValueValidator(0.0)],
        default=0.0,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ('outlet',)
        verbose_name = 'дни доставки и мин сумма'
        verbose_name_plural = 'Дни доставки и мин суммы'

    def __str__(self):
        return (f'{self.outlet} {self.deliveryDate} {self.deadLine} '
                f'{self.minSum}')


class PayForm(models.Model):
    """
    1 - Заказ, 4 - возврат тары
    Тип цены на торговой точке
    """
    payFormExternalCode = models.CharField(
        'Внешний код формы оплаты',
        max_length=NAME_EXT_MAX_LENGHT,
        unique=True,
    )
    payFormName = models.CharField(
        'Название формы оплаты',
        max_length=NAME_EXT_MAX_LENGHT,
        unique=True,
    )
    vatCalculationMode = models.BooleanField(
        'Признак указывающий что необходимо учитывать НДС',
        default=True,
        help_text=('1 – цены в форме оплаты указаны с НДС. '
                   '0 – цены в форме оплаты указаны без НДС, '
                   'поэтому необходимо в портале активировать логику рассечка '
                   'в цены с НДС для отображения в портале')
    )
    orderTypeExternalCode = models.CharField(
        'Заказ/возврат тары',
        max_length=NAME_EXT_MAX_LENGHT,
        default='1',
        help_text='Значения 1-Заказ, 4-возврат тары'
    )

    class Meta:
        ordering = ('payFormName',)
        verbose_name = 'форма оплаты(тип цен)'
        verbose_name_plural = 'Формы оплаты(типов цен)'

    def __str__(self):
        return self.payFormName


class OutletPayForm(models.Model):
    payForm = models.ForeignKey(
        PayForm,
        on_delete=models.CASCADE,
        verbose_name='форма оплаты',
        related_name='payform_outlets',
    )
    outlet = models.ForeignKey(
        Outlet,
        on_delete=models.CASCADE,
        verbose_name='ТТ',
        related_name='outlet_payforms',
        null=True  # CHECKED !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    )

    class Meta:
        ordering = ('payForm',)
        verbose_name = 'форма оплаты по торговой точке'  # Тип цены
        verbose_name_plural = 'форма оплаты по торговым точкам'

    def __str__(self):
        return f'{self.outlet} {self.payForm}'


class PriceList(models.Model):
    payForm = models.ForeignKey(
        PayForm,
        on_delete=models.CASCADE,
        verbose_name='форма оплаты',
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        verbose_name='склад',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='товар',
    )
    productType = models.PositiveSmallIntegerField(
        'тип продукта',
        default=0,
        help_text=('Если на точке синхронизации установлен признак '
                   'isUsePromo=0, то принимается тип продукта:'
                   'для формы оплаты "1 - Заказ"'
                   '- базовый = 0, акционный = 2, критический = 4, '
                   'продукт микс = 7 '
                   'для формы оплаты "4-возврат тары"'
                   '- тара = 8'

                   'Если на точке синхронизации установлен признак '
                   'isUsePromo=1, то принимается тип продукта:'
                   'для формы оплаты "1 - Заказ"'
                   '- базовый = 0'
                   'для формы оплаты "4-возврат тары"'
                   '- тара = 8')
    )

    price = models.FloatField(  # numeric(18,2)
        'цена',
        default=0.0,
        validators=[MinValueValidator(0.0)],
    )
    vat = models.FloatField(  # numeric(5,2)
        'Значение ставки НДС (%)',
        default=0.0,
        validators=[MinValueValidator(0.0)],
    )

    class Meta:
        ordering = ('product',)
        verbose_name = 'цена'
        verbose_name_plural = 'Цены'
        default_related_name = 'prices'
        constraints = (
            models.UniqueConstraint(
                fields=('product', 'warehouse', 'payForm'),
                name='unique_warehouse_product_price'
            ),
        )

    def __str__(self):
        return f'{self.product} {self.price}'


class TypeStatusOrders(models.IntegerChoices):
    RECEIVED = 1, 'Получен'
    SEND_B24 = 2, 'Отправлен в Б24'
    CONFIRMED = 3, 'Подтвержден в Выбирай'
    SHIPPED = 4, 'Отгружен'
    SHIPPED_VYBEERAI = 5, 'Отгружен в Выбирай'
    NOT_COMPLIT = 6, 'Выгружен не полностью'

class Order(models.Model):
    orderNo = models.CharField(
        'Код заказа',
        max_length=NAME_EXT_MAX_LENGHT,
    )
    mainOrderNo = models.TextField(
        'Сводный код заказа',
        help_text=('Код заказа (Код сгенерированный порталом. Объединяет '
                   'несколько заказов. Если один заказ, сделанный на портале, '
                   'разделился на несколько.)')
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        verbose_name='склад',
    )
    outlet = models.ForeignKey(
        Outlet,
        on_delete=models.CASCADE,
        verbose_name='ТТ',
        related_name='orders',
        null=True  # CHECKED !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    )
    payForm = models.ForeignKey(
        PayForm,
        on_delete=models.CASCADE,
        verbose_name='форма оплаты',
    )
    orderTypeExternalCode = models.CharField(
        'Внешний код типа ордера',
        max_length=NAME_EXT_MAX_LENGHT,
        null=True,
        blank=True,
    )
    deliveryDate = models.DateTimeField('Дата доставки заказа')
    totalSum = models.FloatField(  # numeric(18,5)
        'Общая сумма заказа',
        validators=[MinValueValidator(0.0)],
    )
    vatSum = models.FloatField(  # numeric(18,5)
        'Сумма начисленного НДС',
        validators=[MinValueValidator(0.0)],
        default=0.0,
    )
    discount = models.FloatField(  # numeric(9,2)
        'Скидка',
        validators=[MinValueValidator(0.0)],
        default=0.0,
    )
    creationDate = models.DateTimeField('Время и дата оформления заказа')
    operation = models.ForeignKey(
        Operation,
        on_delete=models.CASCADE,
        verbose_name='операция',
    )
    deliveryAddress = models.CharField(
        'Адрес доставки',
        max_length=COMMENT_MAX_LENGHT,
    )
    comment = models.CharField(
        'комментарий',
        max_length=COMMENT_MAX_LENGHT,
    )
    status = models.PositiveSmallIntegerField(
        'Статус',
        choices=TypeStatusOrders.choices,
        default=TypeStatusOrders.RECEIVED,
    )
    code_B24 = models.PositiveIntegerField('Код Битрикс', unique=True,
                                           null=True, default=None)
    isReturn = models.BooleanField('Признак накладной по возврату тары',
                                   default=False)
    #isReturn = models.SmallIntegerField('Признак накладной по возврату тары')
    olCardType = models.SmallIntegerField('где создан заказ')
    #  4 – браузер. 44 – приложение.

    # outletData # Содержит информацию о потенциальном поставщике.

    # orderHPromo Таблица
    # Содержит результаты применения промо акций и/или контрактных
    # условий, которые были совершены мобильным пользователем

    class Meta:
        ordering = ('orderNo',)
        verbose_name = 'заказ'
        verbose_name_plural = 'Заказы'
        default_related_name = 'orders'

    def __str__(self):
        return (f'Заказ: {self.orderNo} склад:{self.warehouse} '
                f'{self.comment[:PRESENTATION_MAX_LENGTH]}')

"""
class OutletData(models.Model):
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        verbose_name='Заказ',
    )
    tempOutletCode = models.CharField(
        'Временный внешний код ТТ',
        max_length=NAME_EXT_MAX_LENGHT,
        unique=True,
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        verbose_name='Компания',
    )
    deliveryAddress = models.CharField(
        'Адрес доставки',
        max_length=COMMENT_MAX_LENGHT,
        blank=True,
    )
    phone = models.CharField(
        'Телефон',
        max_length=NAME_EXT_MAX_LENGHT,
    )
    contactPerson = models.CharField(
        'Контактное лицо',
        max_length=COMMENT_MAX_LENGHT,
        blank=True,
    )

    class Meta:
        ordering = ('tempOutletCode',)
        verbose_name = 'компания в заказе'
        verbose_name_plural = 'Компания в заказах'

    def __str__(self):
        return self.company.legalName
"""

class OrderDetail(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name='Заказ',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='товар',
    )
    price = models.FloatField(  # numeric(18,5)
        'цена',
        validators=[MinValueValidator(0.0)],
    )
    basePrice = models.FloatField(  # numeric(18,5)
        'Цена базового продукта',
        validators=[MinValueValidator(0.0)],
    )
    qty = models.FloatField(  # numeric(18,2)
        'Заказанное количество',
        validators=[MinValueValidator(0.0)],
    )
    vat = models.FloatField(  # numeric(18,2)
        'Ставка НДС(%)',
        validators=[MinValueValidator(0.0)],
        default=0.0,
    )
    discount = models.FloatField(  # numeric(9,2)
        'Процент скидки',
        validators=[MinValueValidator(0.0)],
        default=0.0,
    )
    # isReturnable
    # Количество возвращаемой тары (заполняется когда isReturn заполнено)
    # orderDPromo Таблица
    # Содержит результаты применения промо акций и/или контрактных условий,
    #  которые были совершены пользователем

    class Meta:
        ordering = ('order',)
        verbose_name = 'товар в заказе'
        verbose_name_plural = 'Товары в заказе'
        default_related_name = 'products_in_order'
        constraints = (
            models.UniqueConstraint(
                fields=('order', 'product'),
                name='unique_order_product'
            ),
        )

    def __str__(self):
        return f'{self.order} {self.product} {self.qty}'


#class SyncOrder(models.Model):
#    order = models.OneToOneField(
#        Order,
#        on_delete=models.CASCADE,
#        verbose_name='Заказ',
#        related_name='syncorders',
#    )
#    statusOrder = models.PositiveSmallIntegerField(
#        'Статус состояния заказа',
#        help_text=('1 - новый, 2 - выгружен в Б24, 3 - информация о приёме '
#                   'отправлена в портал'),
#    )
#
#    class Meta:
#        ordering = ('order',)
#        verbose_name = 'статус заказа'
#        verbose_name_plural = 'Статус заказов'

#    def __str__(self):
#        return f'{self.order} {self.statusOrder}'


class Denial(models.Model):
    denialExternalCode = models.CharField(
        'Внешний код причины отказа',
        max_length=NAME_EXT_MAX_LENGHT,
    )
    name = models.CharField(
        'Название причины отказа',
        max_length=NAME_MAX_LENGHT,
    )
    denialCode = models.CharField(
        'Дополнительный Код отказа заказа',
        max_length=NAME_EXT_MAX_LENGHT,
        help_text='если доп кода нет то указывать denialExternalCode'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'причина отказа'
        verbose_name_plural = 'Причины отказа'

    def __str__(self):
        return self.name


class OrderHDenial(models.Model):
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        verbose_name='Заказ',
        related_name='order_denials',
    )
    denial = models.ForeignKey(
        Denial,
        on_delete=models.CASCADE,
        verbose_name='причина отказа',
        related_name='orders_denial',
    )
    #statusOrderDenial = models.PositiveSmallIntegerField(
    #    'Статус состояния отправки причины неудачи',
    #    help_text=('1 - новый, 2 - выгружен в портал'),
    #    default=1
    #)

    class Meta:
        ordering = ('order',)
        verbose_name = 'причина отказа заказа'
        verbose_name_plural = 'Причины отказа заказов'

    def __str__(self):
        return f'{self.order} {self.denial}'


class OrderInvoice(models.Model):
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        verbose_name='Заказ',
        related_name='invoice',
    )
    date = models.DateField('Дата продажи продукции')
    invoiceExternalCode = models.CharField(
        'Внешний код счета/фактуры',
        max_length=NAME_EXT_MAX_LENGHT,
    )
    invoiceNo = models.CharField(
        'Номер счета/фактуры',
        max_length=CODE_EXT_MAX_LENGHT,
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        verbose_name='склад',
        related_name='invoices',
    )
    totalSum = models.FloatField(  # numeric(19,5)
        'Общая сумма отгрузки заказа',
        validators=[MinValueValidator(0.0)],
    )
    vatSum = models.FloatField(  # numeric(19,5)
        'Сумма НДС',
        validators=[MinValueValidator(0.0)],
        default=0.0,
    )

    class Meta:
        ordering = ('order',)
        verbose_name = 'счет/фактура'
        verbose_name_plural = 'Счет/фактуры'

    def __str__(self):
        return f'Счет: {self.invoiceExternalCode} склад: {self.warehouse}'


class SalOutDetail(models.Model):
    orderInvoice = models.ForeignKey(
        OrderInvoice,
        on_delete=models.CASCADE,
        verbose_name='счет/фактура',
        related_name='products_in_invoice',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='товар',
    )
    productQty = models.FloatField(  # numeric(13,3)
        'количество отгруженной продукции',
        validators=[MinValueValidator(0.0)],
    )
    price = models.FloatField(  # numeric(15,8)
        'цена',
        validators=[MinValueValidator(0.0)],
    )
    vat = models.CharField(
        'НДС',
        max_length=CODE_EXT_MAX_LENGHT,
        default='БЕЗ НДС',
    )

    class Meta:
        ordering = ('orderInvoice',)
        verbose_name = 'товар в счете'
        verbose_name_plural = 'Товары в счете'
        constraints = (
            models.UniqueConstraint(
                fields=('orderInvoice', 'product'),
                name='unique_orderInvoice_product'
            ),
        )
