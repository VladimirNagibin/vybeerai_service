# Generated by Django 3.2 on 2024-11-11 17:25

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouses', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productstock',
            name='stock',
            field=models.FloatField(default=0, help_text='Необходимость передачи нулевого значения зависит от: processingType = 0 – можно не передавать processingType = 1 – нужно передавать', validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Остаток на складе'),
        ),
        migrations.AlterField(
            model_name='warehouse',
            name='customerExternalCode',
            field=models.CharField(default=1, help_text='Если точка синхронизации не используется, равно warehouseExternalCode', max_length=50, verbose_name='Внешний код точки синхронизации'),
        ),
    ]
