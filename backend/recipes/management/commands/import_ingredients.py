import json

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('/foodgram', type=str)

    def handle(self, *args, **options):
        with open(options['/foodgram'], encoding="utf8") as f:
            data = json.load(f)
        for item in data:
            Ingredient.objects.create(
                name=item['name'],
                measurement_unit=item['measurement_unit']
            )