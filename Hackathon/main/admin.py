from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import SavedSearch

@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'is_public', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['name', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('user', 'name', 'description')
        }),
        ('검색 조건', {
            'fields': ('search_params',),
            'classes': ('collapse',)
        }),
        ('설정', {
            'fields': ('is_public',)
        }),
        ('메타 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# User 모델 확장
class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('date_joined', 'last_login')
    list_filter = UserAdmin.list_filter + ('date_joined', 'last_login')
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(UserAdmin.readonly_fields)
        if obj:  # 편집 중인 경우
            readonly_fields.extend(['date_joined', 'last_login'])
        return readonly_fields

# 기존 UserAdmin을 CustomUserAdmin으로 교체
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)