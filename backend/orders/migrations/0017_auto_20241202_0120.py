# Generated by Django 3.2 on 2024-12-01 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0016_company_tempoutletcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='realExternalCode',
            field=models.CharField(blank=True, max_length=50, verbose_name='Временный внешний код ТТ'),
        ),
        migrations.AlterField(
            model_name='company',
            name='tempOutletCode',
            field=models.CharField(blank=True, max_length=50, verbose_name='Временный внешний код ТТ'),
        ),
    ]
