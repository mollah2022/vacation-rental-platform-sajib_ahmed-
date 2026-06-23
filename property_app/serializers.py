from rest_framework import serializers
from .models import Location, Property


class LocationSerializer(serializers.ModelSerializer):
    """Serialize location data for API response."""

    class Meta:
        model = Location
        fields = ['id', 'name', 'city', 'state', 'country', 'slug']


class PropertySerializer(serializers.ModelSerializer):
    """Serialize property data for API response."""

    location = LocationSerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            'id', 'title', 'slug', 'property_type', 'status',
            'price', 'bedrooms', 'bathrooms', 'area_sqft',
            'location', 'is_featured', 'primary_image'
        ]

    def get_primary_image(self, obj):
        """Return the first image URL of the property."""
        first_image = obj.images.first()
        if first_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(first_image.image.url)
            return first_image.image.url
        return None


class LocationAutocompleteSerializer(serializers.ModelSerializer):
    """Lightweight serializer for autocomplete suggestions."""

    label = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = ['id', 'name', 'city', 'country', 'slug', 'label']

    def get_label(self, obj):
        """Return a display label for the autocomplete dropdown."""
        return f"{obj.city}, {obj.country}"