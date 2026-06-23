from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from property_app.models import Location


class Command(BaseCommand):
    """Set GPS coordinates and description keywords for locations."""
    help = 'Set location point and description from predefined data'

    def handle(self, *args, **kwargs):
        city_data = {
            "Cox's Bazar": {
                "coords": (21.4272, 92.0058),
                "description": "sea beach ocean coastal waves surf sand resort waterfront swimming diving snorkeling seafood"
            },
            "Bandarban": {
                "coords": (22.1953, 92.2184),
                "description": "hill mountain tribal nature forest trekking adventure waterfall scenic remote indigenous"
            },
            "Dhaka": {
                "coords": (23.8103, 90.4125),
                "description": "city capital urban modern busy shopping mall restaurant nightlife business center"
            },
            "Sylhet": {
                "coords": (24.8949, 91.8687),
                "description": "tea garden lake nature scenic peaceful green hills spiritual shrine waterfall"
            },
            "Rangamati": {
                "coords": (22.6430, 92.1990),
                "description": "lake water boat hill forest nature peaceful tribal scenic kaptai"
            },
            "Panam Nagar": {
                "coords": (23.6273, 90.5590),
                "description": "heritage historic old town colonial architecture culture museum ancient"
            },
            "Barisal": {
                "coords": (22.7010, 90.3535),
                "description": "river boat waterway canal floating market southern delta peaceful"
            },
            "Khagrachhari": {
                "coords": (23.1193, 91.9847),
                "description": "hill forest nature trekking tribal adventure scenic remote mountain"
            },
            "Chittagong": {
                "coords": (22.3569, 91.7832),
                "description": "port city sea coastal beach urban commercial ship industry"
            },
            "Srimangal": {
                "coords": (24.3063, 91.7317),
                "description": "tea garden green nature peaceful forest bird watching eco tourism"
            },
        }

        success_count = 0
        for location in Location.objects.all():
            if location.name in city_data:
                data = city_data[location.name]
                lat, lng = data["coords"]
                location.point = Point(lng, lat, srid=4326)
                location.description = data["description"]
                location.save(update_fields=['point', 'description'])
                self.stdout.write(f'Updated: {location.name}')
                success_count += 1
            else:
                self.stdout.write(f'No data found for: {location.name}')

        self.stdout.write(
            self.style.SUCCESS(f'\nDone! Updated {success_count} locations.')
        )