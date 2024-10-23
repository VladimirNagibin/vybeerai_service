from django.core.management.base import BaseCommand

from api.send_requests import SendRequest


class Command(BaseCommand):
    help = 'Send a request.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS(
            SendRequest.product_warehouses()
        ))

    def add_arguments(self, parser):
        parser.add_argument(
            '-u',
            '--update',
            action='store_true',
            default=False,
            help='Удалить текущего суперпользователя если существует.'
        )
