# Generated by Django 3.2 on 2024-12-03 18:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('warehouses', '0003_alter_warehouse_customerexternalcode'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='warehouse',
            name='outlet',
        ),
        migrations.AddField(
            model_name='outlet',
            name='warehouse',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='outlets', to='warehouses.warehouse', verbose_name='склад'),
        ),
        migrations.AlterField(
            model_name='outlet',
            name='outletName',
            field=models.CharField(max_length=150, verbose_name='Наименование ТТ в 1С'),
        ),
    ]
