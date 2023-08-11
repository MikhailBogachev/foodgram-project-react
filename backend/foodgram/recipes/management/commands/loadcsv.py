from csv import DictReader
import csv

from django.core.management import BaseCommand

from recipes.models import Ingredient

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('csv_file', nargs='+', type=str)

    def handle(self, *args, **options):
        for csv_file in options['csv_file']:
            dataReader = csv.reader(open(csv_file, encoding='utf-8'), delimiter=',')
            for row in dataReader:
                ingr = Ingredient(
                    name = row[0],
                    measurement_unit = row[1]
                )
                ingr.save()
