from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'region', 'rating', 'created_at']
    list_filter = ['rating', 'created_at', 'region']
    search_fields = ['user__username', 'region__name', 'comment']
    ordering = ['-created_at']
