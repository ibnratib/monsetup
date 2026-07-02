from datetime import timedelta

from django.contrib import admin
from django.utils import timezone

from products.models import Product, ProductAttributeValue, ProductImage, Report


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductAttributeValueInline(admin.TabularInline):
    model = ProductAttributeValue
    extra = 0
    readonly_fields = ['attribute', 'value_int', 'value_decimal', 'value_boolean',
                       'value_text', 'value_choice']


@admin.action(description="Booster pour 7 jours")
def boost_7_days(modeladmin, request, queryset):
    queryset.update(is_boosted=True, boost_expires_at=timezone.now() + timedelta(days=7))


@admin.action(description="Booster pour 30 jours")
def boost_30_days(modeladmin, request, queryset):
    queryset.update(is_boosted=True, boost_expires_at=timezone.now() + timedelta(days=30))


@admin.action(description="Retirer le boost")
def remove_boost(modeladmin, request, queryset):
    queryset.update(is_boosted=False, boost_expires_at=None)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'category', 'ville', 'status', 'condition', 'price',
                    'is_boosted', 'created_at')
    list_filter = ('status', 'condition', 'category', 'ville', 'is_boosted')
    search_fields = ('title', 'seller__email')
    inlines = [ProductImageInline, ProductAttributeValueInline]
    actions = [boost_7_days, boost_30_days, remove_boost]


@admin.action(description="Marquer comme traitée")
def mark_as_traitee(modeladmin, request, queryset):
    queryset.update(status='TRAITEE')


@admin.action(description="Rejeter")
def mark_as_rejetee(modeladmin, request, queryset):
    queryset.update(status='REJETEE')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('product', 'reporter', 'reason', 'status', 'created_at')
    list_filter = ('reason', 'status')
    search_fields = ('product__title', 'reporter__email')
    actions = [mark_as_traitee, mark_as_rejetee]
