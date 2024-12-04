# Generated by Django 3.2 on 2024-12-04 12:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('warehouses', '0005_auto_20241204_1857'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outlet',
            name='warehouse',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='outlets', to='warehouses.warehouse', verbose_name='склад'),
        ),
    ]
