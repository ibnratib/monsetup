from django.contrib import admin

from catalog.models import AttributeChoice, AttributeDefinition, Category


class AttributeChoiceInline(admin.TabularInline):
    model = AttributeChoice
    extra = 1


class AttributeDefinitionInline(admin.TabularInline):
    model = AttributeDefinition
    extra = 1
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'order')
    list_filter = ('parent',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [AttributeDefinitionInline]


@admin.register(AttributeDefinition)
class AttributeDefinitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'attribute_type', 'required', 'filterable', 'depends_on_choice')
    list_filter = ('category', 'attribute_type')
    inlines = [AttributeChoiceInline]
    raw_id_fields = ('depends_on_choice',)


@admin.register(AttributeChoice)
class AttributeChoiceAdmin(admin.ModelAdmin):
    list_display = ('attribute', 'value', 'order')
    list_filter = ('attribute',)
