# Generated by Django 3.2 on 2024-12-04 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouses', '0006_alter_outlet_warehouse'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='outlet',
            options={'ordering': ('outletName',), 'verbose_name': 'компания', 'verbose_name_plural': 'Компании'},
        ),
        migrations.AddField(
            model_name='outlet',
            name='code_B24',
            field=models.PositiveIntegerField(default=None, null=True, unique=True, verbose_name='Код Битрикс'),
        ),
        migrations.AddField(
            model_name='outlet',
            name='contactPerson',
            field=models.CharField(blank=True, max_length=255, verbose_name='Контактное лицо'),
        ),
        migrations.AddField(
            model_name='outlet',
            name='deliveryAddress',
            field=models.CharField(blank=True, max_length=255, verbose_name='Адрес доставки'),
        ),
        migrations.AddField(
            model_name='outlet',
            name='inn',
            field=models.CharField(blank=True, max_length=50, verbose_name='ИНН'),
        ),
        migrations.AddField(
            model_name='outlet',
            name='legalName',
            field=models.CharField(blank=True, max_length=255, verbose_name='Юридическое название'),
        ),
        migrations.AddField(
            model_name='outlet',
            name='phone',
            field=models.CharField(blank=True, max_length=50, verbose_name='Телефон'),
        ),
        migrations.AddField(
            model_name='outlet',
            name='realExternalCode',
            field=models.CharField(blank=True, max_length=50, verbose_name='Код в УС'),
        ),
        migrations.AddField(
            model_name='outlet',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Получен'), (2, 'Получен код УС'), (3, 'Отправлен код УС')], default=1, verbose_name='Статус'),
        ),
        migrations.AddField(
            model_name='outlet',
            name='tempOutletCode',
            field=models.CharField(blank=True, max_length=50, verbose_name='Временный внешний код ТТ'),
        ),
    ]
