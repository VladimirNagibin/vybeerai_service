# Generated by Django 3.2 on 2024-10-11 14:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_auto_20241011_1711'),
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
        migrations.AlterModelOptions(
            name='syncorder',
            options={'ordering': ('order',), 'verbose_name': 'статус заказа', 'verbose_name_plural': 'Статус заказов'},
        ),
        migrations.AlterField(
            model_name='syncorder',
            name='order',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='syncorders', to='orders.order', verbose_name='Заказ'),
        ),
        migrations.CreateModel(
            name='OrderHDenial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('denial', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders_denial', to='orders.denial', verbose_name='Заказ')),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='order_denials', to='orders.order', verbose_name='Заказ')),
            ],
            options={
                'verbose_name': 'причина отказа заказа',
                'verbose_name_plural': 'Причины отказа заказов',
                'ordering': ('order',),
            },
        ),
    ]
