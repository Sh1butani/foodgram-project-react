import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """
    Django-команда для импорта ингредиентов
    из CSV-файла в базу данных.
    """

    help = 'Загрузка csv файлов в базу данных'

    def import_ingridient(self):
        if Ingredient.objects.exists():
            print('Данные ингридиентов уже загружены.')
        else:
            with open(
                settings.BASE_DIR / 'data/ingredients.csv',
                'r',
                encoding='utf8',
                newline=''
            ) as file:
                reader = csv.DictReader(file)
                for row in reader:
                    Ingredient.objects.create(
                        name=row['name'],
                        measurement_unit=row['measurement unit']
                    )
                print('Данные ингридиентов успешно загружены!')

    def handle(self, *args, **kwargs):
        self.import_ingridient()
