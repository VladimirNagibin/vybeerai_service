# Generated by Django 3.2 on 2024-12-04 14:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0020_auto_20241204_0154'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='outletdata',
            name='company',
        ),
        migrations.RemoveField(
            model_name='outletdata',
            name='order',
        ),
        migrations.DeleteModel(
            name='Company',
        ),
        migrations.DeleteModel(
            name='OutletData',
        ),
    ]
