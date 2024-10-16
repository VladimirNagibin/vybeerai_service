import csv

from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import IntegrityError, connection

from orders.models import (DeliveryDate, Denial, Operation, OperationOutlet,
                           Order, OrderDetail, OrderHDenial, OrderInvoice,
                           OutletPayForm, PayForm, PriceList, SalOutDetail,
                           SyncOrder)
from products.models import (Attribut, AttributValue, Package, Pictograph,
                             Product, ProductAttributValue, ProductImages)
from warehouses.models import Outlet, Warehouse, ProductStock


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
    ('outlet.csv',
     Outlet,
     ['id', 'outletExternalCode', 'outletName']),
    ('warehouse.csv',
     Warehouse,
     ['id', 'warehouseExternalCode', 'customerExternalCode', 'warehouseName',
      'outlet_id']),
    ('productStock.csv',
     ProductStock,
     ['id', 'warehouse_id', 'product_id', 'stock']),
    ('operation.csv',
     Operation,
     ['id', 'operationExternalCode', 'operationName']),
    ('operationOutlet.csv',
     OperationOutlet,
     ['id', 'operation_id', 'warehouse_id', 'stock']),
    ('deliveryDate.csv',
     DeliveryDate,
     ['id', 'warehouse_id', 'deliveryDate', 'deadLine', 'minSum']),
    ('payForm.csv',
     PayForm,
     ['id', 'payFormExternalCode', 'payFormName']),
    ('outletPayForm.csv',
     OutletPayForm,
     ['id', 'payForm_id', 'warehouse_id']),
    ('priceList.csv',
     PriceList,
     ['id', 'payForm_id', 'warehouse_id', 'product_id', 'price']),
    ('order.csv',
     Order,
     ['id', 'orderNo', 'warehouse_id', 'payForm_id', 'deliveryDate',
      'totalSum', 'creationDate', 'operation_id', 'deliveryAddress',
      'comment', 'isReturn', 'oLCardType']),
    ('orderDetail.csv',
     OrderDetail,
     ['id', 'order_id', 'product_id', 'price', 'basePrice', 'qty']),
    ('syncOrder.csv',
     SyncOrder,
     ['id', 'order_id', 'statusOrder']),
    ('denial.csv',
     Denial,
     ['id', 'denialExternalCode', 'name', 'denialCode']),
    ('orderHDenial.csv',
     OrderHDenial,
     ['id', 'order_id', 'denial_id', 'statusOrderDenial']),
    ('orderInvoice.csv',
     OrderInvoice,
     ['id', 'order_id', 'date', 'invoiceExternalCode', 'invoiceNo',
      'warehouse_id', 'totalSum']),
    ('salOutDetail.csv',
     SalOutDetail,
     ['id', 'orderInvoice_id', 'product_id', 'productQty', 'price']),
    ('productImages.csv',
     ProductImages,
     ['id', 'product_id', 'image']),
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
