from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'read_status', 'sent_at')
    list_filter = ('type', 'read_status', 'sent_at')
    search_fields = ('user__username', 'message')

