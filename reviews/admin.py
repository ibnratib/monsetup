from django.contrib import admin

from reviews.models import Review, ReviewReply, ReviewReport, ReviewTag


@admin.register(ReviewTag)
class ReviewTagAdmin(admin.ModelAdmin):
    list_display = ('label',)
    search_fields = ('label',)


class ReviewReplyInline(admin.StackedInline):
    model = ReviewReply
    extra = 0
    max_num = 1


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'seller', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('reviewer__email', 'seller__email')
    inlines = [ReviewReplyInline]
    raw_id_fields = ('reviewer', 'seller')


@admin.action(description="Marquer comme traitée")
def mark_treated(modeladmin, request, queryset):
    queryset.update(status='TRAITEE')


@admin.action(description="Rejeter")
def mark_rejected(modeladmin, request, queryset):
    queryset.update(status='REJETEE')


@admin.register(ReviewReport)
class ReviewReportAdmin(admin.ModelAdmin):
    list_display = ('review', 'reporter', 'reason', 'status', 'created_at')
    list_filter = ('reason', 'status')
    search_fields = ('reporter__email',)
    actions = [mark_treated, mark_rejected]
    raw_id_fields = ('reporter', 'review')
