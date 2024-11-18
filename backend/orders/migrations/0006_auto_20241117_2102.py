# Generated by Django 3.2 on 2024-11-17 14:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('warehouses', '0003_alter_warehouse_customerexternalcode'),
        ('orders', '0005_auto_20241117_1919'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='deliveryDate',
            field=models.DateTimeField(verbose_name='Дата доставки заказа'),
        ),
        migrations.AlterField(
            model_name='order',
            name='warehouse',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='warehouses.warehouse', verbose_name='склад'),
        ),
    ]