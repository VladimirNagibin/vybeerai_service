from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from core.constants import (CLASSIFICATION_CODE_DEFAULT, CODE_EXT_MAX_LENGHT,
                            EAN_MAX_LENGHT, NAME_MAX_LENGHT, PACK_MAX_LENGHT,
                            PRESENTATION_MAX_LENGTH)


class Package(models.Model):
    packageName = models.CharField(
        'Тип единицы измерения',
        max_length=PACK_MAX_LENGHT,
        help_text='Тип единицы измерения(например: бутылка или банка или кег)',
    )

    class Meta:
        ordering = ('packageName',)
        verbose_name = 'тип единицы измерения'
        verbose_name_plural = 'Типы единиц измерения'

    def __str__(self):
        return self.packageName[:PRESENTATION_MAX_LENGTH]


class Pictograph(models.Model):
    pictograph = models.PositiveSmallIntegerField('Пиктограмма')
    pictographName = models.CharField(
        'Наименование пиктограммы',
        max_length=PACK_MAX_LENGHT,
    )
    # Справочные значения:
    # 1 - бутылка,
    # 2 - банка,
    # 3 - кег,
    # 4 - тетрапак,
    # 5 - заморозка,
    # 6 - мороженное,
    # 7 - промо набор,
    # 8 - жвачка,
    # 9 - шоколадки,
    # 10 - леденцы,
    # 11 - снеки, сухарики,
    # 12 - чипсы,
    # 13 - чай,
    # 14 - торты,
    # 15 - соль, приправы,
    # 16 - сигареты,
    # 17 - семечки,
    # 18 - рыбка,
    # 19 - рулет,
    # 20 - приправы,
    # 21 - презервативы,
    # 22 - пирожное,
    # 23 - печенье,
    # 24 - орешки,
    # 25 - мука,
    # 26 - макароны,
    # 27 - майонез,
    # 28 - лапша, картофель быстрого приготовления,
    # 29 - крупа,
    # 30 - кофе,
    # 31 - корм для животных,
    # 32 - конфеты,
    # 33 - консервы,
    # 34 - кетчуп, соус в бут.,
    # 35 - зажигалки, мундштук,
    # 36 - все сладости,
    # 37 - сахар,
    # 38 - батарейки,
    # 39 - Туалетная бумага,
    # 40 - Салфетки/полотенца бумажные,
    # 41 - Салфетки влажные,
    # 42 - Чистящие/моющие средства (для ванны, для унитаза, для кухни),
    # 43 - Шампунь/Бальзам для волос,
    # 44 - Гель для душа /Пена для ванн,
    # 45 - Мыло кусковое,
    # 46 - Мыло жидкое,
    # 47 - Подгузники,
    # 48 - Ватные диски,
    # 49 - Стиральный порошок,
    # 50 - Зубная паста,
    # 51 - Зубные щетки,
    # 52 - Крема для лица,
    # 53 - Крема для рук и тела,
    # 54 - Губка д/мытья посуды,
    # 55 - Кондиционер для белья/Отбеливатель,
    # 56 - Краска для волос/Маска для волос,
    # 57 - Мешки для мусора/Пакеты,
    # 58 - Освежитель воздуха,
    # 59 - Скатерть,
    # 60 - Детское питание,
    # 61 - Выпечка/Сдоба,
    # 62 - Бублик/Сушки/Баранки/Крендель,
    # 63 - Джем/Топпинг,
    # 64 - Попкорн,
    # 65 - Игрушки со сладостями.
    # Для дополнительных параметров обратиться в техническую поддержку.

    class Meta:
        ordering = ('pictographName',)
        verbose_name = 'пиктограмма'
        verbose_name_plural = 'Пиктограммы'

    def __str__(self):
        return self.pictographName[:PRESENTATION_MAX_LENGTH]


class Product(models.Model):
    productExternalCode = models.CharField(
        'Код в 1С',
        max_length=CODE_EXT_MAX_LENGHT,
        unique=True,
    )
    eanCode = models.CharField(
        'Штрихкод',
        max_length=EAN_MAX_LENGHT,
        null=True,
        blank=True,
    )
    productExternalName = models.CharField(
        'Наименование в 1С',
        max_length=NAME_MAX_LENGHT,
        unique=True,
    )
    productName = models.CharField(
        'Наименование',
        max_length=NAME_MAX_LENGHT,
        unique=True,
        help_text='Наименование для выгрузки в Выбирай',
    )
    productClassificationExternalCode = models.CharField(
        'Внешний код классификации продукта',
        max_length=EAN_MAX_LENGHT,
        default=CLASSIFICATION_CODE_DEFAULT,
        help_text=('Внешний код классификации продукта. В текущей версии '
                   'указывать значение "1"')
    )
    volume = models.FloatField(  # numeric(12, 4)
        'Базовый объем',
        validators=[MinValueValidator(0.0)])
    package = models.ForeignKey(
        Package,
        on_delete=models.CASCADE,
        verbose_name='Тип единицы измерения',
        related_name='products',
        help_text='Тип единицы измерения(например: бутылка или банка или кег)',
    )
    packageQty = models.FloatField(  # numeric(12, 4)
        'Кол-во ед товара в уп',
        validators=[MinValueValidator(0.0)],
        help_text='Количество базовых единиц товара в упаковке',
    )
    description = models.TextField('Описание продукта')
    isTare = models.BooleanField('Продукция является тарой', default=False)
    pictograph = models.ForeignKey(
        Pictograph,
        on_delete=models.CASCADE,
        verbose_name='Пиктограмма',
        related_name='products',
    )
    productSegmentExternalCode = models.CharField(
        'Внешний код сегмента',
        max_length=PACK_MAX_LENGHT,
        null=True,
        blank=True,
        help_text=('Данный код должен быть уникальным ключем для объединения '
                   'данных по сегменту.'),
    )
    # productExternalCode2 = models.CharField(
    #    'Код продукта',
    #    max_length=EAN_MAX_LENGHT,
    #    null=True,
    #    blank=True,
    # )
    # productTechnicalName = models.CharField(
    #    'Техническое название продукта',
    #    max_length=NAME_MAX_LENGHT,
    #    null=True,
    #    blank=True,
    # )
    # isAlc = models.BooleanField(
    #    'Продукция является алкоголем',
    #    default=False,
    #    null=True,
    #    blank=True,
    # )
    # IsSouvenir = models.BooleanField(
    #    'Продукция является сувениром',
    #    default=False,
    #    null=True,
    #    blank=True,
    # )

    class Meta:
        ordering = ('productName',)
        verbose_name = 'товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.productName[:PRESENTATION_MAX_LENGTH]

    def clean(self):
        ...
        # attributs = [attr_value.attributValue.attribut for
        #             attr_value in self.attribut_values.all()]
        # if len(attributs) != len(set(attributs)):
        #    raise ValidationError('Выбрано несколько значений одного атрибута')


class Attribut(models.Model):
    attributsName = models.CharField(
        'Наименование',
        max_length=PACK_MAX_LENGHT
    )
    attributsNameSortOrder = models.IntegerField(
        'Порядок сортировки',
        null=True,
        blank=True,
        help_text='Порядок сортировки атрибута в разделе фильтров',
    )
    isFilter = models.BooleanField(
        'Признак отображения в фильтрах',
        help_text=('Признак отображения атрибута в разделе фильтров на форме '
                   'каталога'),
    )
    isCardDetailsProduct = models.BooleanField(
        'Признак отображения в карточке',
        help_text='Признак отображения атрибута в карточке товаров',
    )

    class Meta:
        verbose_name = 'атрибут'
        verbose_name_plural = 'Атрибуты'

    def __str__(self):
        return self.attributsName[:PRESENTATION_MAX_LENGTH]


class AttributValue(models.Model):
    attribut = models.ForeignKey(
        Attribut,
        on_delete=models.CASCADE,
        verbose_name='атрибут',
        related_name='attributes_value',
    )
    attributsValue = models.CharField(
        'Значение атрибута',
        max_length=PACK_MAX_LENGHT
    )
    attributsValueSortOrder = models.IntegerField(
        'Порядок сортировки значений атрибута',
        null=True,
        blank=True,
        help_text=('Порядок сортировки значений атрибута при формировании '
                   'фильтров в разделе фильтрации')
    )

    class Meta:
        verbose_name = 'значение атрибута'
        verbose_name_plural = 'Значения атрибутов'

    def __str__(self):
        return f'{self.attribut.attributsName} {self.attributsValue}'


class ProductAttributValue(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Товар',
        related_name='attribut_values',
    )
    attributValue = models.ForeignKey(
        AttributValue,
        on_delete=models.CASCADE,
        verbose_name='Значение атрибута',
        related_name='attribut_values',
    )

    class Meta:
        verbose_name = 'значение атрибута товара'
        verbose_name_plural = 'Значения атрибутов товаров'

    def __str__(self):
        return f'{self.product} {self.attributValue}'

    def clean(self):
        if ProductAttributValue.objects.filter(
            product=self.product,
            attributValue__attribut=self.attributValue.attribut
        ).count() > 1:
            print('DUBLE')


class ProductImages(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Товар',
        related_name='images',
    )
    image = models.ImageField('Image', upload_to='images')

    class Meta:
        verbose_name = 'изображение товара'
        verbose_name_plural = 'Изображения'

    def __str__(self):
        return (f'{self.product.productName[:PRESENTATION_MAX_LENGTH]} '
                f'{self.image}')
