# Generated by Django 3.2 on 2024-11-11 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouses', '0002_auto_20241112_0025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='warehouse',
            name='customerExternalCode',
            field=models.CharField(default='1', help_text='Если точка синхронизации не используется, равно warehouseExternalCode', max_length=50, verbose_name='Внешний код точки синхронизации'),
        ),
    ]
