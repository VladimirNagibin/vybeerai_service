# Generated by Django 3.2 on 2024-12-25 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_auto_20241206_0003'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='attribut',
            options={'verbose_name': 'атрибут', 'verbose_name_plural': '\u200b\u200b\u200bАтрибуты'},
        ),
        migrations.AlterModelOptions(
            name='attributvalue',
            options={'verbose_name': 'значение атрибута', 'verbose_name_plural': '\u200b\u200b\u200b\u200bЗначения атрибутов'},
        ),
        migrations.AlterModelOptions(
            name='groupproduct',
            options={'ordering': ('name',), 'verbose_name': 'группа', 'verbose_name_plural': '\u200bГруппы'},
        ),
        migrations.AlterModelOptions(
            name='package',
            options={'ordering': ('packageName',), 'verbose_name': 'тип единицы измерения', 'verbose_name_plural': '\u200b\u200b\u200b\u200b\u200bТипы единиц измерения'},
        ),
        migrations.AlterModelOptions(
            name='pictograph',
            options={'ordering': ('pictographName',), 'verbose_name': 'пиктограмма', 'verbose_name_plural': '\u200b\u200b\u200b\u200b\u200b\u200bПиктограммы'},
        ),
        migrations.AlterModelOptions(
            name='productimages',
            options={'verbose_name': 'изображение товара', 'verbose_name_plural': '\u200b\u200bИзображения'},
        ),
        migrations.AlterField(
            model_name='productimages',
            name='image',
            field=models.ImageField(upload_to='images', verbose_name='Изображение'),
        ),
    ]
