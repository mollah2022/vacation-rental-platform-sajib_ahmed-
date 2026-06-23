import os
import sys
import django
import pandas as pd
import requests
from django.contrib.gis.geos import Point
from django.core.files.base import ContentFile

sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from property_app.models import Location, Property, PropertyImage


def download_image(url, filename):
    """Download image from URL and return as ContentFile."""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return ContentFile(response.content, name=filename)
        print(f"  Failed to download image: HTTP {response.status_code}")
        return None
    except Exception as e:
        print(f"  Failed to download image: {e}")
        return None


def get_or_create_location(row):
    """Find existing location by city and country, or create a new one."""
    slug = f"{row['city'].lower().replace(' ', '-')}-{row['country'].lower().replace(' ', '-')}"

    location, created = Location.objects.get_or_create(
        slug=slug,
        defaults={
            'name': row['city'],
            'city': row['city'],
            'state': row['state'],
            'country': row['country'],
            'is_active': True,
        }
    )

    if created:
        print(f"  Created location: {location.name}, {location.country}")
    else:
        print(f"  Found existing location: {location.name}, {location.country}")

    return location


def import_properties(csv_file_path):
    """Read CSV file and save each row as a Property in the database."""
    print(f"Reading CSV file: {csv_file_path}")
    df = pd.read_csv(csv_file_path)
    print(f"Found {len(df)} properties in CSV\n")

    success_count = 0
    skip_count = 0

    for index, row in df.iterrows():
        print(f"Processing row {index + 1}: {row['title']}")

        # Skip if property with same title already exists
        if Property.objects.filter(title=row['title']).exists():
            print(f"  Skipped — property already exists\n")
            skip_count += 1
            continue

        # Get or create location for this property
        location = get_or_create_location(row)

        # Build GPS point from latitude and longitude columns
        point = None
        if pd.notna(row['latitude']) and pd.notna(row['longitude']):
            point = Point(float(row['longitude']), float(row['latitude']), srid=4326)

        # Create the property record
        property_obj = Property.objects.create(
            location=location,
            title=row['title'],
            description=row['description'],
            property_type=row['property_type'],
            status=row['status'],
            price=row['price'],
            bedrooms=int(row['bedrooms']),
            bathrooms=int(row['bathrooms']),
            area_sqft=row['area_sqft'] if pd.notna(row['area_sqft']) else None,
            address=row['address'],
            point=point,
            is_active=True,
        )

        # Download and save image if URL is provided
        if 'image_url' in row and pd.notna(row['image_url']):
            print(f"  Downloading image...")
            filename = f"property_{property_obj.id}.jpg"
            image_file = download_image(row['image_url'], filename)
            if image_file:
                PropertyImage.objects.create(
                    property=property_obj,
                    image=image_file,
                    is_primary=True,
                    sort_order=0,
                    alt_text=property_obj.title
                )
                print(f"  Image saved!")

        print(f"  Saved property: {property_obj.title}\n")
        success_count += 1

    print(f"Import complete!")
    print(f"  Saved: {success_count} properties")
    print(f"  Skipped: {skip_count} properties (already existed)")


if __name__ == '__main__':
    csv_path = '/app/data/properties.csv'
    import_properties(csv_path)