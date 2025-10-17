from django.contrib import admin
# from .models import ChatSession, ChatMessage

# @admin.register(ChatSession)
# class ChatSessionAdmin(admin.ModelAdmin):
#     list_display = ['session_id', 'user', 'created_at', 'updated_at', 'is_active']
#     list_filter = ['is_active', 'created_at', 'user']
#     search_fields = ['session_id', 'user__username']
#     ordering = ['-created_at']

# @admin.register(ChatMessage)
# class ChatMessageAdmin(admin.ModelAdmin):
#     list_display = ['session', 'message_type', 'content', 'timestamp']
#     list_filter = ['message_type', 'timestamp', 'session']
#     search_fields = ['content', 'session__session_id']
#     ordering = ['-timestamp']
