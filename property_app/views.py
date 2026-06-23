from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db import models as django_models
from django.contrib.gis.db.models.functions import Distance
from .models import Location, Property, PropertyImage
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import LocationAutocompleteSerializer


def home(request):
    """Homepage with search form and featured properties."""
    featured_properties = Property.objects.filter(
        is_featured=True, is_active=True
    ).select_related('location')[:6]

    recent_properties = Property.objects.filter(
        is_active=True
    ).select_related('location')[:8]

    locations = Location.objects.filter(is_active=True)

    context = {
        'featured_properties': featured_properties,
        'recent_properties': recent_properties,
        'locations': locations,
        'property_types': Property.PROPERTY_TYPE_CHOICES,
    }
    return render(request, 'property_app/home.html', context)


def property_list(request):
    """Property listing page with search, filter and pagination."""
    properties = Property.objects.filter(is_active=True).select_related('location')


    # Search by city, country or property name (combined text + semantic search)
    search = request.GET.get('search', '')
    if search:
        from .services import combined_location_search

        # Get matching locations using combined search (text + semantic)
        matched_locations = combined_location_search(search, limit=20)

        # Filter properties by matched locations OR by title
        properties = properties.filter(
            django_models.Q(location__in=matched_locations) |
            django_models.Q(title__icontains=search)
        )

    # Filter by property type
    property_type = request.GET.get('property_type', '')
    if property_type:
        properties = properties.filter(property_type=property_type)

    # Filter by max price
    max_price = request.GET.get('max_price', '')
    if max_price:
        properties = properties.filter(price__lte=max_price)

    # Filter by bedrooms
    bedrooms = request.GET.get('bedrooms', '')
    if bedrooms:
        properties = properties.filter(bedrooms__gte=bedrooms)

    # Pagination — 6 properties per page
    paginator = Paginator(properties, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search': search,
        'property_type': property_type,
        'max_price': max_price,
        'bedrooms': bedrooms,
        'property_types': Property.PROPERTY_TYPE_CHOICES,
        'total_count': properties.count(),
    }
    return render(request, 'property_app/property_list.html', context)


def property_detail(request, slug):
    """Property detail page with images and distance from city center."""
    property = get_object_or_404(Property, slug=slug, is_active=True)
    images = property.images.all()

    # Calculate distance from city center if property has GPS point
    distance_km = None
    if property.point and property.location.point:
        property_point = property.point
        city_point = property.location.point
        distance = property_point.distance(city_point)
        # Convert to km (distance() returns degrees, so use Distance properly)
        from django.contrib.gis.measure import D
        qs = Property.objects.filter(pk=property.pk).annotate(
            dist=Distance('point', city_point)
        )
        if qs.exists():
            distance_km = round(qs.first().dist.km, 2)

    # Get similar properties from same location
    similar_properties = Property.objects.filter(
        location=property.location,
        is_active=True
    ).exclude(pk=property.pk)[:3]

    context = {
        'property': property,
        'images': images,
        'distance_km': distance_km,
        'similar_properties': similar_properties,
    }
    return render(request, 'property_app/property_detail.html', context)


@api_view(['GET'])
def location_autocomplete(request):
    """
    API endpoint for location autocomplete using semantic search.
    Usage: /api/locations/autocomplete/?q=beach
    Returns top 5 matching locations as JSON.
    """
    query = request.GET.get('q', '').strip()

    # Return empty list if query is too short
    if len(query) < 2:
        return Response([])

    from .services import combined_location_search
    locations = combined_location_search(query, limit=5)

    serializer = LocationAutocompleteSerializer(locations, many=True)
    return Response(serializer.data)

