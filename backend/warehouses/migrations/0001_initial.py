# Generated by Django 3.2 on 2024-10-22 06:58

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Outlet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('outletExternalCode', models.CharField(max_length=50, unique=True, verbose_name='Внешний код ТТ')),
                ('outletName', models.CharField(max_length=150, unique=True, verbose_name='Наименование ТТ в 1С')),
            ],
            options={
                'verbose_name': 'торговая точка',
                'verbose_name_plural': 'Торговые точки',
                'ordering': ('outletName',),
            },
        ),
        migrations.CreateModel(
            name='Warehouse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('warehouseExternalCode', models.CharField(max_length=50, unique=True, verbose_name='Код склада в 1С')),
                ('customerExternalCode', models.CharField(help_text='Если точка синхронизации не используется, равно warehouseExternalCode', max_length=50, unique=True, verbose_name='Внешний код точки синхронизации')),
                ('warehouseName', models.CharField(max_length=50, unique=True, verbose_name='Наименование склада')),
                ('allowTareReturn', models.BooleanField(blank=True, default=False, null=True, verbose_name='Allow tare return')),
                ('outlet', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='warehouses', to='warehouses.outlet', verbose_name='Торговая точка')),
            ],
            options={
                'verbose_name': 'склад',
                'verbose_name_plural': 'Склады',
                'ordering': ('warehouseName',),
            },
        ),
        migrations.CreateModel(
            name='ProductStock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock', models.FloatField(help_text='Необходимость передачи нулевого значения зависит от: processingType = 0 – можно не передавать processingType = 1 – нужно передавать', validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Остаток на складе')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_stocks', to='products.product', verbose_name='товар')),
                ('warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_stocks', to='warehouses.warehouse', verbose_name='склад')),
            ],
            options={
                'verbose_name': 'остатки товаров на складах',
                'verbose_name_plural': 'Остатки товаров на складах',
                'ordering': ('warehouse', 'product'),
            },
        ),
        migrations.AddConstraint(
            model_name='productstock',
            constraint=models.UniqueConstraint(fields=('warehouse', 'product'), name='unique_warehouse_product'),
        ),
    ]
