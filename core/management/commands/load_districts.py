import json
from django.core.management.base import BaseCommand
from core.models import District

class Command(BaseCommand):
    help = 'Load district data from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **kwargs):
        with open(kwargs['file'], 'r') as f:
            data = json.load(f)
            for feature in data['features']:
                properties = feature['properties']
                District.objects.create(
                    dtname=properties['dtname'],
                    stname=properties['stname'],
                    stcode11=properties['stcode11'],
                    dtcode11=properties['dtcode11'],
                    year_stat=properties['year_stat'],
                    objectid=properties['objectid'],
                    dist_lgd=properties['dist_lgd'],
                    state_lgd=properties['state_lgd'],
                    coordinates=feature['geometry']
                )
        self.stdout.write(self.style.SUCCESS('Successfully loaded district data.'))
