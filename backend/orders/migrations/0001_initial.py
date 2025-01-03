# Generated by Django 3.2 on 2024-10-22 06:58

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('warehouses', '0001_initial'),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Denial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('denialExternalCode', models.CharField(max_length=50, verbose_name='Внешний код причины отказа')),
                ('name', models.CharField(max_length=150, verbose_name='Название причины отказа')),
                ('denialCode', models.CharField(help_text='если доп кода нет то указывать denialExternalCode', max_length=50, verbose_name='Дополнительный Код отказа заказа')),
            ],
            options={
                'verbose_name': 'причина отказа',
                'verbose_name_plural': 'Причины отказа',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Operation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operationExternalCode', models.CharField(max_length=50, verbose_name='Внешний код Типа операции')),
                ('operationName', models.CharField(max_length=50, verbose_name='Название Типа операции')),
                ('coefficient', models.FloatField(default=1.0, help_text='Значение влияет на общую суму заказа (поле является пользовательским). Для нулевого влияния указывать значение “1”.', validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Коэффициент ')),
            ],
            options={
                'verbose_name': 'операция',
                'verbose_name_plural': 'Операции',
                'ordering': ('operationName',),
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('orderNo', models.CharField(max_length=50, verbose_name='Код заказа')),
                ('mainOrderNo', models.TextField(help_text='Код заказа (Код сгенерированный порталом. Объединяет несколько заказов. Если один заказ, сделанный на портале, разделился на несколько.)', verbose_name='Сводный код заказа')),
                ('orderTypeExternalCode', models.CharField(blank=True, max_length=50, null=True, verbose_name='Внешний код типа ордера')),
                ('deliveryDate', models.DateField(verbose_name='Дата доставки заказа')),
                ('totalSum', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Общая сумма заказа')),
                ('vatSum', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Сумма начисленного НДС')),
                ('discount', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Скидка')),
                ('creationDate', models.DateTimeField(verbose_name='Время и дата оформления заказа')),
                ('deliveryAddress', models.CharField(max_length=255, verbose_name='Адрес доставки')),
                ('comment', models.CharField(max_length=255, verbose_name='комментарий')),
                ('isReturn', models.SmallIntegerField(verbose_name='Признак накладной по возврату тары')),
                ('oLCardType', models.SmallIntegerField(verbose_name='где создан заказ')),
                ('operation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='orders.operation', verbose_name='операция')),
            ],
            options={
                'verbose_name': 'заказ',
                'verbose_name_plural': 'Заказы',
                'ordering': ('orderNo',),
                'default_related_name': 'orders',
            },
        ),
        migrations.CreateModel(
            name='OrderInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Дата продажи продукции')),
                ('invoiceExternalCode', models.CharField(max_length=50, verbose_name='Внешний код счета/фактуры')),
                ('invoiceNo', models.CharField(max_length=100, verbose_name='Номер счета/фактуры')),
                ('totalSum', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Общая сумма отгрузки заказа')),
                ('vatSum', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Сумма НДС')),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='invoice', to='orders.order', verbose_name='Заказ')),
                ('warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='warehouses.warehouse', verbose_name='склад')),
            ],
            options={
                'verbose_name': 'счет/фактура',
                'verbose_name_plural': 'Счет/фактуры',
                'ordering': ('order',),
            },
        ),
        migrations.CreateModel(
            name='PayForm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payFormExternalCode', models.CharField(max_length=50, unique=True, verbose_name='Внешний код формы оплаты')),
                ('payFormName', models.CharField(max_length=50, unique=True, verbose_name='Название формы оплаты')),
                ('vatCalculationMode', models.BooleanField(default=True, help_text='1 – цены в форме оплаты указаны с НДС. 0 – цены в форме оплаты указаны без НДС, поэтому необходимо в портале активировать логику рассечка в цены с НДС для отображения в портале', verbose_name='Признак указывающий что необходимо учитывать НДС')),
                ('orderTypeExternalCode', models.CharField(default='1', help_text='Значения 1-Заказ, 4-возврат тары', max_length=50, verbose_name='Заказ/возврат тары')),
            ],
            options={
                'verbose_name': 'форма оплаты(тип цен)',
                'verbose_name_plural': 'Формы оплаты(типов цен)',
                'ordering': ('payFormName',),
            },
        ),
        migrations.CreateModel(
            name='SyncOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('statusOrder', models.PositiveSmallIntegerField(help_text='1 - новый, 2 - выгружен в Б24, 3 - информация о приёме отправлена в портал', verbose_name='Статус состояния заказа')),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='syncorders', to='orders.order', verbose_name='Заказ')),
            ],
            options={
                'verbose_name': 'статус заказа',
                'verbose_name_plural': 'Статус заказов',
                'ordering': ('order',),
            },
        ),
        migrations.CreateModel(
            name='SalOutDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('productQty', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='количество отгруженной продукции')),
                ('price', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='цена')),
                ('vat', models.CharField(default='БЕЗ НДС', max_length=100, verbose_name='НДС')),
                ('orderInvoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products_in_invoice', to='orders.orderinvoice', verbose_name='счет/фактура')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product', verbose_name='товар')),
            ],
            options={
                'verbose_name': 'товар в счете',
                'verbose_name_plural': 'Товары в счете',
                'ordering': ('orderInvoice',),
            },
        ),
        migrations.CreateModel(
            name='PriceList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('productType', models.PositiveSmallIntegerField(default=0, help_text='Если на точке синхронизации установлен признак isUsePromo=0, то принимается тип продукта:для формы оплаты "1 - Заказ"- базовый = 0, акционный = 2, критический = 4, продукт микс = 7 для формы оплаты "4-возврат тары"- тара = 8Если на точке синхронизации установлен признак isUsePromo=1, то принимается тип продукта:для формы оплаты "1 - Заказ"- базовый = 0для формы оплаты "4-возврат тары"- тара = 8', verbose_name='тип продукта')),
                ('price', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='цена')),
                ('vat', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Значение ставки НДС (%)')),
                ('payForm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='orders.payform', verbose_name='форма оплаты')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='products.product', verbose_name='товар')),
                ('warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='warehouses.warehouse', verbose_name='склад')),
            ],
            options={
                'verbose_name': 'цена',
                'verbose_name_plural': 'Цены',
                'ordering': ('product',),
                'default_related_name': 'prices',
            },
        ),
        migrations.CreateModel(
            name='OutletPayForm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payForm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payform_outlets', to='orders.payform', verbose_name='форма оплаты')),
                ('warehouse', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payforms_outlet', to='warehouses.warehouse', verbose_name='склад')),
            ],
            options={
                'verbose_name': 'форма оплаты по торговой точке',
                'verbose_name_plural': 'форма оплаты по торговым точкам',
                'ordering': ('payForm',),
            },
        ),
        migrations.CreateModel(
            name='OrderHDenial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('statusOrderDenial', models.PositiveSmallIntegerField(default=1, help_text='1 - новый, 2 - выгружен в портал', verbose_name='Статус состояния отправки причины неудачи')),
                ('denial', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders_denial', to='orders.denial', verbose_name='причина отказа')),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='order_denials', to='orders.order', verbose_name='Заказ')),
            ],
            options={
                'verbose_name': 'причина отказа заказа',
                'verbose_name_plural': 'Причины отказа заказов',
                'ordering': ('order',),
            },
        ),
        migrations.CreateModel(
            name='OrderDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='цена')),
                ('basePrice', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Цена базового продукта')),
                ('qty', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Заказанное количество')),
                ('vat', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Ставка НДС(%)')),
                ('discount', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Процент скидки')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products_in_order', to='orders.order', verbose_name='Заказ')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products_in_order', to='products.product', verbose_name='товар')),
            ],
            options={
                'verbose_name': 'товар в заказе',
                'verbose_name_plural': 'Товары в заказе',
                'ordering': ('order',),
                'default_related_name': 'products_in_order',
            },
        ),
        migrations.AddField(
            model_name='order',
            name='payForm',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='orders.payform', verbose_name='форма оплаты'),
        ),
        migrations.AddField(
            model_name='order',
            name='warehouse',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='warehouses.warehouse', verbose_name='склад'),
        ),
        migrations.CreateModel(
            name='OperationOutlet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='operatin_outlets', to='orders.operation', verbose_name='операция')),
                ('warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='operations_outlet', to='warehouses.warehouse', verbose_name='склад')),
            ],
            options={
                'verbose_name': 'операция по торговой точке',
                'verbose_name_plural': 'Операции по торговым точкам',
                'ordering': ('warehouse', 'operation'),
            },
        ),
        migrations.CreateModel(
            name='DeliveryDate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deliveryDate', models.CharField(blank=True, default='Пн, Вт, Ср, Чт, Пт', max_length=50, null=True, verbose_name='Дни доставки')),
                ('deadLine', models.CharField(blank=True, default='17:00', max_length=20, null=True, verbose_name='Граничное времени обработки заказа')),
                ('minSum', models.FloatField(blank=True, default=0.0, null=True, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Минимальная сумма заказа')),
                ('warehouse', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='delivery_dates', to='warehouses.warehouse', verbose_name='склад')),
            ],
            options={
                'verbose_name': 'дни доставки и мин сумма',
                'verbose_name_plural': 'Дни доставки и мин суммы',
                'ordering': ('warehouse',),
            },
        ),
        migrations.AddConstraint(
            model_name='saloutdetail',
            constraint=models.UniqueConstraint(fields=('orderInvoice', 'product'), name='unique_orderInvoice_product'),
        ),
        migrations.AddConstraint(
            model_name='pricelist',
            constraint=models.UniqueConstraint(fields=('product', 'warehouse', 'payForm'), name='unique_warehouse_product_price'),
        ),
        migrations.AddConstraint(
            model_name='orderdetail',
            constraint=models.UniqueConstraint(fields=('order', 'product'), name='unique_order_product'),
        ),
        migrations.AddConstraint(
            model_name='operationoutlet',
            constraint=models.UniqueConstraint(fields=('warehouse', 'operation'), name='unique_warehouse_operation'),
        ),
    ]
