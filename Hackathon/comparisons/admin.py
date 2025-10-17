from django.contrib import admin
from .models import Comparison

@admin.register(Comparison)
class ComparisonAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'user', 'category', 'is_favorite', 
        'regions_count', 'created_at'
    ]
    list_filter = [
        'category', 'is_favorite', 'created_at'
    ]
    search_fields = ['user__username', 'name']
    ordering = ['-created_at']
    list_editable = ['is_favorite']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('user', 'name', 'category')
        }),
        ('설정', {
            'fields': ('is_favorite',)
        }),
        ('비교 지역', {
            'fields': ('regions',)
        }),
        ('메타 정보', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    filter_horizontal = ['regions']
    
    def regions_count(self, obj):
        return obj.regions.count()
    regions_count.short_description = '비교 지역 수'
