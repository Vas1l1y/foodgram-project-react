from django.contrib import admin

# Register your models here.
from .models import Ingredient, Tag


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'measurement_unit']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Table settings for resource 'Tag' on the admin site."""
    list_display = ['id', 'name', 'color', 'slug']
    # search_fields = ('name',)
