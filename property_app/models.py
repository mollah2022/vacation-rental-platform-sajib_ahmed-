from django.contrib.gis.db import models
from django.utils.text import slugify
from pgvector.django import VectorField
# Create your models here.

class Location(models.Model):
    """
    Store location info like city, country and map coordinates.
    """
    name = models.CharField(max_length=225)
    slug = models.SlugField(unique=True)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100)
    address = models.CharField(blank=True)
    point = models.PointField(
        geography=True,
        srid=4326,
        null=True,
        blank=True
    )
    boundary = models.MultiPolygonField(
        srid=4326,
        null=True,
        blank=True
    )
    embedding = VectorField(
        dimensions=1536,
        null=True,
        blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['name']   # Sort locations by name
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'

    def __str__(self):
        return f"{self.name}, {self.city}, {self.country}"

    def save(self, *args, **kwargs):
        # Auto generate slug from name if not given
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Property(models.Model):
    """
    Store vacation rental property info like price, 
    rooms and map location.
    """
    PROPERTY_TYPE_CHOICES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('villa', 'Villa'),
        ('cabin', 'Cabin'),
        ('condo', 'Condo'),
        ('cottage', 'Cottage'),
        ('studio', 'Studio'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),        # Property is live and bookable
        ('inactive', 'Inactive'),    # Property is hidden
        ('pending', 'Pending'),      # Property is under review

    ]

    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='properties'
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    property_type = models.CharField(
        max_length=50,
        choices=PROPERTY_TYPE_CHOICES,
        default='apartment'
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='active'
    )
    price = models.DecimalField(max_digits=14, decimal_places=2)
    bedrooms = models.PositiveSmallIntegerField(default=0)
    bathrooms = models.PositiveSmallIntegerField(default=0)
    area_sqft = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    address = models.TextField(blank=True)
    point = models.PointField(
        geography=True,
        srid=4326,
        null=True,
        blank=True
    )

    footprint = models.PolygonField(
        srid=1536,
        null=True,
        blank=True
    )
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']   # Show newest properties first
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'

    def __str__(self):
        return f"{self.title} - {self.location.city}"

    def save(self, *args, **kwargs):
        # Auto generate slug from title if not given
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class PropertyImage(models.Model):
    """
    Store images for each property. One property can have many images.
    """
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='image'
    )

    image = models.ImageField(upload_to='properties/%Y/%m/')
    alt_text = models.CharField(max_length=255, blank=True)
    caption = models.PositiveIntegerField(null=True, blank=True)
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    embedding = VectorField(
        dimensions=768,
        null=True,
        blank=True
    )

    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)   

    class Meta:
        ordering = ['sort_order', '-created_at']   # Sort by order, then newest first
        verbose_name = 'Property Image'
        verbose_name_plural = 'Property Image'

    def __str__(self):
        return f"Image for {self.property.title} (#{self.sort_order})"

