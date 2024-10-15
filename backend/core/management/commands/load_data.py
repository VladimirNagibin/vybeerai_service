import csv

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import IntegrityError, connection

from products.models import (Package, Pictograph, Product, Attribut,
                             AttributValue, ProductAttributValue)
# from users.models import SubscriptionUser

User = get_user_model()

DIR_DATA = 'data'
DATA = (
    ('package.csv',
     Package,
     ['id', 'packageName']),
    ('pictograph.csv',
     Pictograph,
     ['id', 'pictograph', 'pictographName']),
    ('product.csv',
     Product,
     ['id', 'productExternalCode', 'eanCode', 'productExternalName',
      'productName', 'volume', 'package_id', 'description',
      'pictograph_id']),
    ('attribut.csv',
     Attribut,
     ['id', 'attributsName', 'attributsNameSortOrder', 'isFilter',
      'isCardDetailsProduct']),
    ('attributValue.csv',
     AttributValue,
     ['id', 'attribut_id', 'attributsValue', 'attributsValueSortOrder']),
    ('productAttributValue.csv',
     ProductAttributValue,
     ['id', 'product_id', 'attributValue_id']),
)


class Command(BaseCommand):

    def load_obj(self, filename, obj, fields):
        try:
            with open(f'{DIR_DATA}/{filename}', encoding='utf-8') as file_data:
                reader = csv.reader(file_data, escapechar='/')
                for row in reader:
                    object_value = {
                        key: value for key, value in zip(fields, row)
                    }
                    try:
                        object, _ = obj.objects.update_or_create(
                            **object_value
                        )
                        if obj == User:
                            object.set_password(object_value['password'])
                            object.save()
                    except IntegrityError:
                        self.stdout.write(f'Файл {filename} не корректные '
                                          f'данные: {object_value} для '
                                          f'{obj.__name__}')
        except FileNotFoundError:
            self.stdout.write(f'Файл {filename} невозможно открыть')
        except Exception as e:
            self.stdout.write(f'Ошибка {e} при работе с файлом {filename}')
        self.stdout.write(f'Файл {filename} загружен')

    def handle(self, *args, **kwargs):
        models = []
        for filename, obj, fields in DATA:
            if kwargs['erase']:
                obj.objects.all().delete()
            self.load_obj(filename, obj, fields)
            models.append(obj)
        sequence_sql = connection.ops.sequence_reset_sql(no_style(), models)
        with connection.cursor() as cursor:
            for sql in sequence_sql:
                cursor.execute(sql)

    def add_arguments(self, parser):
        parser.add_argument(
            '-e',
            '--erase',
            action='store_true',
            default=False,
            help='Очистить таблицу перед загрузкой'
        )