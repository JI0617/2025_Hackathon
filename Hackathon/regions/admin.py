from django.contrib import admin
from .models import Region, News

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'traffic_score', 'education_score', 'cost_level', 'population', 'area']
    list_filter = ['cost_level', 'traffic_score', 'education_score']
    search_fields = ['name', 'description']
    ordering = ['name']

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'region', 'published_at', 'is_featured']
    list_filter = ['is_featured', 'published_at', 'region']
    search_fields = ['title', 'content']
    ordering = ['-published_at']
