# from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from core.constants import (NAME_EXT_MAX_LENGHT, DEAD_LINE_MAX_LENGHT,
                            NAME_MAX_LENGHT, COMMENT_MAX_LENGHT,
                            PRESENTATION_MAX_LENGTH)
from products.models import Product
from warehouses.models import Warehouse


class Operation(models.Model):
    """Наличный, Безналичный, По условиям договора"""
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
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        verbose_name='склад',
        related_name='operations_outlet',
    )

    class Meta:
        ordering = ('operation',)
        verbose_name = 'операция по торговой точке'
        verbose_name_plural = 'Операции по торговым точкам'
        constraints = (
            models.UniqueConstraint(
                fields=('warehouse', 'operation'),
                name='unique_warehouse_operation'
            ),
        )

    def __str__(self):
        return f'{self.operation} {self.warehouse}'


class DeliveryDate(models.Model):
    warehouse = models.OneToOneField(
        Warehouse,
        on_delete=models.CASCADE,
        verbose_name='склад',
        related_name='delivery_dates',
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
        ordering = ('warehouse',)
        verbose_name = 'дни доставки и мин сумма'
        verbose_name_plural = 'Дни доставки и мин суммы'

    def __str__(self):
        return (f'{self.warehouse} {self.deliveryDate} {self.deadLine} '
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
    warehouse = models.OneToOneField(
        Warehouse,
        on_delete=models.CASCADE,
        verbose_name='склад',
        related_name='payforms_outlet',
    )

    class Meta:
        ordering = ('payForm',)
        verbose_name = 'форма оплаты по торговой точке'  # Тип цены
        verbose_name_plural = 'форма оплаты по торговым точкам'
        constraints = (
            models.UniqueConstraint(
                fields=('warehouse', 'payForm'),
                name='unique_warehouse_payForm'
            ),
        )

    def __str__(self):
        return f'{self.payForm} {self.warehouse}'


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
        validators=[MinValueValidator(0.0)],
    )
    vat = models.FloatField(  # numeric(5,2)
        'Значение ставки НДС (%)',
        validators=[MinValueValidator(0.0)],
    )

    class Meta:
        ordering = ('product',)
        verbose_name = 'цена'
        verbose_name_plural = 'Цены'
        default_related_name = 'prices'
        constraints = (
            models.UniqueConstraint(
                fields=('warehouse', 'payForm'),
                name='unique_warehouse_product_price'
            ),
        )

    def __str__(self):
        return f'{self.payForm} {self.warehouse}'


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
    warehouse = models.OneToOneField(
        Warehouse,
        on_delete=models.CASCADE,
        verbose_name='склад',
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
    deliveryDate = models.DateField('Дата доставки заказа')
    totalSum = models.FloatField(  # numeric(18,5)
        'Общая сумма заказа',
        validators=[MinValueValidator(0.0)],
    )
    vatSum = models.FloatField(  # numeric(18,5)
        'Сумма начисленного НДС',
        validators=[MinValueValidator(0.0)],
    )
    discount = models.FloatField(  # numeric(9,2)
        'Скидка',
        validators=[MinValueValidator(0.0)],
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
    isReturn = models.SmallIntegerField('Признак накладной по возврату тары')
    oLCardType = models.SmallIntegerField('где создан заказ')
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
        return f'{self.orderNo} {self.warehouse}'


class orderDetail(models.Model):
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
        'Ставка НДС',
        validators=[MinValueValidator(0.0)],
    )
    discount = models.FloatField(  # numeric(9,2)
        'Процент скидки',
        validators=[MinValueValidator(0.0)],
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

    def __str__(self):
        return f'{self.orderNo} {self.warehouse}'


class SyncOrder(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name='Заказ',
        related_name='products',
    )
    statusOrder = models.PositiveSmallIntegerField(
        'Статус состояния заказа',
        help_text=('1 - новый, 2 - выгружен в Б24, 3 - информация о приёме '
                   'отправлена в портал'),
    )
