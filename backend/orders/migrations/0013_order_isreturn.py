# Generated by Django 3.2 on 2024-11-19 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0012_remove_order_isreturn'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='isReturn',
            field=models.BooleanField(default=False, verbose_name='Признак накладной по возврату тары'),
        ),
    ]
