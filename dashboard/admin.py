from django.contrib import admin

from dashboard.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'is_read', 'product', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('message', 'user__email')
    raw_id_fields = ('user', 'product')
    readonly_fields = ('created_at', 'updated_at')
