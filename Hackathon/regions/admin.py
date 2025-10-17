from django.contrib import admin
from .models import Region, News

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'city', 'traffic_score', 'education_score', 
        'medical_score', 'cost_level', 'population', 'area'
    ]
    list_filter = [
        'city', 'cost_level', 'traffic_score', 'education_score', 
        'medical_score', 'created_at'
    ]
    search_fields = ['name', 'city', 'description']
    ordering = ['city', 'name']
    list_editable = ['traffic_score', 'education_score', 'medical_score', 'cost_level']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('name', 'city', 'description', 'image_url')
        }),
        ('점수 정보', {
            'fields': ('traffic_score', 'education_score', 'medical_score', 'cost_level')
        }),
        ('지리 정보', {
            'fields': ('population', 'area', 'latitude', 'longitude')
        }),
        ('메타 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'region', 'category', 'published_at', 
        'is_featured', 'is_realtime', 'priority'
    ]
    list_filter = [
        'is_featured', 'is_realtime', 'category', 'published_at', 
        'region', 'priority'
    ]
    search_fields = ['title', 'content', 'region__name']
    ordering = ['-priority', '-published_at']
    list_editable = ['is_featured', 'is_realtime', 'priority']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'content', 'region')
        }),
        ('분류 및 우선순위', {
            'fields': ('category', 'priority')
        }),
        ('상태 설정', {
            'fields': ('is_featured', 'is_realtime')
        }),
        ('외부 링크', {
            'fields': ('source_url',)
        }),
        ('메타 정보', {
            'fields': ('published_at',),
            'classes': ('collapse',)
        }),
    )
