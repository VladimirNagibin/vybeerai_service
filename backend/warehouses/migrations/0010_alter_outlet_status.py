# Generated by Django 3.2 on 2024-12-05 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouses', '0009_alter_outlet_code_b24'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outlet',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Получен'), (2, 'Получен код УС'), (3, 'Отправлен код в Выбирай'), (4, 'Отменён в Выбирай')], default=1, verbose_name='Статус'),
        ),
    ]