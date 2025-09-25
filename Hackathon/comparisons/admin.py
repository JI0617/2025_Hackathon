from django.contrib import admin
from .models import Comparison

@admin.register(Comparison)
class ComparisonAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'name']
    ordering = ['-created_at']
