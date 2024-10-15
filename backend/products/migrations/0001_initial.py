# Generated by Django 3.2 on 2024-10-11 16:31

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attribut',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attributsName', models.CharField(max_length=100, verbose_name='Наименование')),
                ('attributsNameSortOrder', models.IntegerField(blank=True, help_text='Порядок сортировки атрибута в разделе фильтров', null=True, verbose_name='Порядок сортировки')),
                ('isFilter', models.BooleanField(help_text='Признак отображения атрибута в разделе фильтров на форме каталога', verbose_name='Признак отображения в фильтрах')),
                ('isCardDetailsProduct', models.BooleanField(help_text='Признак отображения атрибута в карточке товаров', verbose_name='Признак отображения в карточке')),
            ],
            options={
                'verbose_name': 'атрибут',
                'verbose_name_plural': 'Атрибуты',
            },
        ),
        migrations.CreateModel(
            name='AttributValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attributsValue', models.CharField(max_length=100, verbose_name='Значение атрибута')),
                ('attributsValueSortOrder', models.IntegerField(blank=True, help_text='Порядок сортировки значений атрибута при формировании фильтров в разделе фильтрации', null=True, verbose_name='Порядок сортировки значений атрибута')),
                ('attribut', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attributes_value', to='products.attribut', verbose_name='атрибут')),
            ],
            options={
                'verbose_name': 'значение атрибута',
                'verbose_name_plural': 'Значения атрибутов',
            },
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('packageName', models.CharField(help_text='Тип единицы измерения(например: бутылка или банка или кег)', max_length=100, verbose_name='Тип единицы измерения')),
            ],
            options={
                'verbose_name': 'тип единицы измерения',
                'verbose_name_plural': 'Типы единиц измерения',
                'ordering': ('packageName',),
            },
        ),
        migrations.CreateModel(
            name='Pictograph',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pictograph', models.PositiveSmallIntegerField(verbose_name='Пиктограмма')),
                ('pictographName', models.CharField(max_length=100, verbose_name='Наименование пиктограммы')),
            ],
            options={
                'verbose_name': 'пиктограмма',
                'verbose_name_plural': 'Пиктограммы',
                'ordering': ('pictographName',),
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('productExternalCode', models.CharField(max_length=100, unique=True, verbose_name='Код в 1С')),
                ('eanCode', models.CharField(blank=True, max_length=50, null=True, verbose_name='Штрихкод')),
                ('productExternalName', models.CharField(max_length=150, unique=True, verbose_name='Наименование в 1С')),
                ('productName', models.CharField(help_text='Наименование для выгрузки в Выбирай', max_length=150, unique=True, verbose_name='Наименование')),
                ('productClassificationExternalCode', models.CharField(default='1', help_text='Внешний код классификации продукта. В текущей версии указывать значение "1"', max_length=50, verbose_name='Внешний код классификации продукта')),
                ('volume', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Базовый объем')),
                ('packageQty', models.FloatField(help_text='Количество базовых единиц товара в упаковке', validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Кол-во ед товара в уп')),
                ('description', models.TextField(verbose_name='Описание продукта')),
                ('isTare', models.BooleanField(default=False, verbose_name='Продукция является тарой')),
                ('productSegmentExternalCode', models.CharField(blank=True, help_text='Данный код должен быть уникальным ключем для объединения данных по сегменту.', max_length=100, null=True, verbose_name='Внешний код сегмента')),
                ('package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='products.package', verbose_name='Тип единицы измерения')),
                ('pictograph', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='products.pictograph', verbose_name='Пиктограмма')),
            ],
            options={
                'verbose_name': 'товар',
                'verbose_name_plural': 'Товары',
                'ordering': ('productName',),
            },
        ),
        migrations.CreateModel(
            name='ProductImages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='images', verbose_name='Image')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='products.product', verbose_name='Товар')),
            ],
            options={
                'verbose_name': 'изображение товара',
                'verbose_name_plural': 'Изображения',
            },
        ),
        migrations.CreateModel(
            name='ProductAttributValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attributValue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attribut_values', to='products.attributvalue', verbose_name='Значение атрибута')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attribut_values', to='products.product', verbose_name='Товар')),
            ],
            options={
                'verbose_name': 'значение атрибута товара',
                'verbose_name_plural': 'Значения атрибутов товаров',
            },
        ),
    ]