from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from property_app.models import Location, Property


class Command(BaseCommand):
    """Set GPS coordinates for locations based on their properties GPS data."""
    help = 'Set location point from average of property points'

    def handle(self, *args, **kwargs):
        locations = Location.objects.all()

        # Manually defined GPS coordinates for each city
        city_coordinates = {
            "Cox's Bazar": (21.4272, 92.0058),
            "Bandarban": (22.1953, 92.2184),
            "Dhaka": (23.8103, 90.4125),
            "Sylhet": (24.8949, 91.8687),
            "Rangamati": (22.6430, 92.1990),
            "Panam Nagar": (23.6273, 90.5590),
            "Barisal": (22.7010, 90.3535),
            "Khagrachhari": (23.1193, 91.9847),
            "Chittagong": (22.3569, 91.7832),
            "Srimangal": (24.3063, 91.7317),
        }

        success_count = 0
        for location in locations:
            if location.name in city_coordinates:
                lat, lng = city_coordinates[location.name]
                location.point = Point(lng, lat, srid=4326)
                location.save(update_fields=['point'])
                self.stdout.write(f'Set point for: {location.name} ({lat}, {lng})')
                success_count += 1
            else:
                self.stdout.write(f'No coordinates found for: {location.name}')

        self.stdout.write(
            self.style.SUCCESS(f'\nDone! Set points for {success_count} locations.')
        )