from django.contrib import admin
from .models import UserPreference

@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'traffic_importance', 'education_importance', 
        'medical_importance', 'cost_importance', 'preferred_cost_level',
        'deposit_budget', 'monthly_rent_budget'
    ]
    list_filter = [
        'traffic_importance', 'education_importance', 'medical_importance',
        'cost_importance', 'preferred_cost_level', 'created_at'
    ]
    search_fields = ['user__username', 'user__email']
    ordering = ['user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('사용자', {
            'fields': ('user',)
        }),
        ('중요도 설정', {
            'fields': (
                'traffic_importance', 'education_importance', 
                'medical_importance', 'cost_importance'
            )
        }),
        ('선호 설정', {
            'fields': ('preferred_cost_level',)
        }),
        ('예산 설정', {
            'fields': ('deposit_budget', 'monthly_rent_budget')
        }),
        ('메타 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
