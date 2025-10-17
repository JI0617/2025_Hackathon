from django.contrib import admin
from .models import Policy

@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'category', 'region', 'is_active', 
        'is_featured', 'priority', 'created_at'
    ]
    list_filter = [
        'category', 'region', 'is_active', 'is_featured',
        'created_at', 'application_start', 'application_end'
    ]
    search_fields = ['title', 'content', 'summary']
    list_editable = ['is_active', 'is_featured', 'priority']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'summary', 'content')
        }),
        ('분류', {
            'fields': ('category', 'region')
        }),
        ('대상자', {
            'fields': (
                'target_age_min', 'target_age_max',
                'target_income_min', 'target_income_max'
            )
        }),
        ('지원 내용', {
            'fields': ('support_amount', 'support_period', 'support_type')
        }),
        ('신청 정보', {
            'fields': (
                'application_start', 'application_end',
                'application_url', 'contact_info'
            )
        }),
        ('상태 관리', {
            'fields': ('is_active', 'is_featured', 'priority')
        }),
        ('메타 정보', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # 새로 생성하는 경우
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
