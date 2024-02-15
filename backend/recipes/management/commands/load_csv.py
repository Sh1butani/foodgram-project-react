import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    """
    Django-команда для импорта CSV-файлов в базу данных.
    """
    help = 'Загрузка CSV-файлов в базу данных.'

    def import_ingredient(self):
        if Ingredient.objects.all().exists():
            print('Данные ингредиентов уже загружены.')
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
                print('Данные ингредиентов успешно загружены!')

    def import_tags(self):
        if Tag.objects.all().exists():
            print('Данные тэгов уже загружены.')
        else:
            with open(
                settings.BASE_DIR / 'data/tags.csv',
                'r',
                encoding='utf8',
                newline=''
            ) as file:
                reader = csv.DictReader(file)
                for row in reader:
                    Tag.objects.create(
                        name=row['name'],
                        color=row['color'],
                        slug=row['slug']
                    )
                print('Данные тэгов успешно загружены!')

    def handle(self, *args, **kwargs):
        self.import_ingredient()
        self.import_tags()
