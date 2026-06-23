from django.core.management.base import BaseCommand
from sentence_transformers import SentenceTransformer
from property_app.models import Location


class Command(BaseCommand):
    """Management command to generate embeddings for all locations."""
    help = 'Generate sentence transformer embeddings for all locations'

    def handle(self, *args, **kwargs):
        # Load the sentence transformer model
        self.stdout.write('Loading sentence transformer model...')
        model = SentenceTransformer('all-MiniLM-L6-v2')
        self.stdout.write(self.style.SUCCESS('Model loaded!'))

        # Get all active locations
        locations = Location.objects.filter(is_active=True)
        total = locations.count()
        self.stdout.write(f'Found {total} locations to process...')

        success_count = 0

        for location in locations:
            # Build text to embed — combine name, city, state, country
            text = f"{location.name} {location.city} {location.state} {location.country} {location.description}"
            text = text.strip()

            # Generate 384-dimension vector from text
            embedding = model.encode(text).tolist()

            # Save embedding to database
            location.embedding = embedding
            location.save(update_fields=['embedding'])

            self.stdout.write(f'  Generated embedding for: {location.name}, {location.country}')
            success_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'\nDone! Generated embeddings for {success_count}/{total} locations.')
        )