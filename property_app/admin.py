from django.contrib.gis import admin
from django.utils.html import format_html
from .models import Location, Property, PropertyImage


class PropertyImageInline(admin.TabularInline):
    """Show property images inside the property edit page."""
    model = PropertyImage
    extra = 1
    fields = ['image', 'image_preview', 'alt_text', 'is_primary', 'sort_order']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        """Show a small thumbnail of the image in admin."""
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="70" style="object-fit:cover; border-radius:4px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview'


@admin.register(Location)
class LocationAdmin(admin.GISModelAdmin):
    """Admin panel for Location model with map support."""
    list_display = ['name', 'city', 'state', 'country', 'is_active', 'created_at']
    list_filter = ['country', 'state', 'is_active']
    search_fields = ['name', 'city', 'country']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']
    readonly_fields = ['embedding']  # AI generated, not editable from admin


@admin.register(Property)
class PropertyAdmin(admin.GISModelAdmin):
    """Admin panel for Property with map, filters and image preview."""
    list_display = ['title', 'property_type', 'status', 'price', 'bedrooms', 'bathrooms', 'location', 'is_featured', 'is_active']
    list_filter = ['property_type', 'status', 'is_featured', 'is_active', 'location__country', 'location__city']
    search_fields = ['title', 'description', 'address']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['-created_at']
    inlines = [PropertyImageInline]
    list_editable = ['is_featured', 'is_active']
    readonly_fields = ['embedding']  # AI generated, not editable from admin


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    """Admin panel for PropertyImage with image preview."""
    list_display = ['property', 'image_preview', 'is_primary', 'sort_order', 'created_at']
    list_filter = ['is_primary']
    search_fields = ['property__title', 'alt_text']
    ordering = ['property', 'sort_order']
    readonly_fields = ['embedding']  # AI generated, not editable from admin

    def image_preview(self, obj):
        """Show a small thumbnail of the image in admin list view."""
        if obj.image:
            return format_html(
                '<img src="{}" width="80" height="60" style="object-fit:cover; border-radius:4px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview'