from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from accounts.models import Boutique, Particulier, User


class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'user_type', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('user_type', 'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'phone_whatsapp', 'user_type')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'user_type', 'password1', 'password2'),
        }),
    )


@admin.register(Particulier)
class ParticulierAdmin(admin.ModelAdmin):
    list_display = ('user', 'max_active_ads', 'created_at')
    raw_id_fields = ('user',)


@admin.register(Boutique)
class BoutiqueAdmin(admin.ModelAdmin):
    list_display = ('nom_boutique', 'slug', 'statut_verification', 'created_at')
    list_filter = ('statut_verification',)
    search_fields = ('nom_boutique', 'user__email')
    prepopulated_fields = {'slug': ('nom_boutique',)}
    raw_id_fields = ('user',)


admin.site.register(User, UserAdmin)
