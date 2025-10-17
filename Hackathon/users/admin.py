from django.contrib import admin
from .models import UserPreference

@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'traffic_importance', 'education_importance', 'cost_importance', 'preferred_cost_level']
    list_filter = ['traffic_importance', 'education_importance', 'cost_importance', 'preferred_cost_level']
    search_fields = ['user__username', 'user__email']
    ordering = ['user__username']
