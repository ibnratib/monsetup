import json

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from catalog.models import AttributeChoice, AttributeDefinition, Category
from products.models import Product


class StaffRequiredMixin(UserPassesTestMixin):
    """Only staff/superuser can access the admin panel."""

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def handle_no_permission(self):
        return redirect('login')


# ──────────────────────── Dashboard ────────────────────────


class DashboardView(StaffRequiredMixin, View):
    def get(self, request):
        context = {
            'total_products': Product.objects.count(),
            'total_categories': Category.objects.count(),
            'total_subcategories': Category.objects.filter(parent__isnull=False).count(),
            'total_attributes': AttributeDefinition.objects.count(),
        }
        return render(request, 'adminpanel/dashboard.html', context)


# ──────────────────────── Categories CRUD ────────────────────────


class CategoryListView(StaffRequiredMixin, View):
    def get(self, request):
        root_categories = Category.objects.filter(
            parent__isnull=True,
        ).prefetch_related('children', 'children__attributes').order_by('order', 'name')
        return render(request, 'adminpanel/categories/list.html', {
            'root_categories': root_categories,
        })


class CategoryCreateView(StaffRequiredMixin, View):
    def get(self, request):
        parents = Category.objects.filter(parent__isnull=True).order_by('order', 'name')
        return render(request, 'adminpanel/categories/form.html', {
            'parents': parents,
            'title': 'Créer une catégorie',
        })

    def post(self, request):
        name = request.POST.get('name', '').strip()
        parent_id = request.POST.get('parent', '').strip()
        icon = request.POST.get('icon', '').strip()
        order = request.POST.get('order', '0').strip()

        if not name:
            messages.error(request, 'Le nom est obligatoire.')
            return redirect('adminpanel:category-create')

        parent = None
        if parent_id:
            parent = get_object_or_404(Category, pk=parent_id)

        try:
            order_val = int(order)
        except (ValueError, TypeError):
            order_val = 0

        Category.objects.create(name=name, parent=parent, icon=icon, order=order_val)
        messages.success(request, f'Catégorie « {name} » créée.')
        return redirect('adminpanel:category-list')


class CategoryEditView(StaffRequiredMixin, View):
    def get(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        parents = Category.objects.filter(parent__isnull=True).exclude(pk=pk).order_by('order', 'name')
        return render(request, 'adminpanel/categories/form.html', {
            'category': category,
            'parents': parents,
            'title': f'Modifier « {category.name} »',
        })

    def post(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        name = request.POST.get('name', '').strip()
        parent_id = request.POST.get('parent', '').strip()
        icon = request.POST.get('icon', '').strip()
        order = request.POST.get('order', '0').strip()

        if not name:
            messages.error(request, 'Le nom est obligatoire.')
            return redirect('adminpanel:category-edit', pk=pk)

        category.name = name
        category.parent = get_object_or_404(Category, pk=parent_id) if parent_id else None
        category.icon = icon
        try:
            category.order = int(order)
        except (ValueError, TypeError):
            category.order = 0
        category.slug = ''  # force re-generation
        category.save()
        messages.success(request, f'Catégorie « {name} » modifiée.')
        return redirect('adminpanel:category-list')


class CategoryDeleteView(StaffRequiredMixin, View):
    def post(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        name = category.name
        category.delete()
        messages.success(request, f'Catégorie « {name} » supprimée.')
        return redirect('adminpanel:category-list')


# ──────────────────────── Attributes CRUD ────────────────────────


class AttributeListView(StaffRequiredMixin, View):
    def get(self, request, cat_pk):
        category = get_object_or_404(Category, pk=cat_pk)
        attributes = category.attributes.prefetch_related('choices').order_by('order', 'name')
        return render(request, 'adminpanel/attributes/list.html', {
            'category': category,
            'attributes': attributes,
        })


class AttributeCreateView(StaffRequiredMixin, View):
    def get(self, request, cat_pk):
        category = get_object_or_404(Category, pk=cat_pk)
        available_choices = self._get_available_choices(category)
        return render(request, 'adminpanel/attributes/form.html', {
            'category': category,
            'available_choices': available_choices,
            'title': f'Ajouter un attribut à « {category.name} »',
        })

    def post(self, request, cat_pk):
        category = get_object_or_404(Category, pk=cat_pk)
        data = request.POST
        try:
            attr = AttributeDefinition(
                category=category,
                name=data.get('name', '').strip(),
                label_fr=data.get('label_fr', '').strip(),
                attribute_type=data.get('attribute_type', 'TEXT_SHORT'),
                required=data.get('required') == 'on',
                filterable=data.get('filterable') == 'on',
                order=int(data.get('order', 0)),
                unit=data.get('unit', '').strip(),
            )
            min_val = data.get('min_value', '').strip()
            max_val = data.get('max_value', '').strip()
            if min_val:
                attr.min_value = min_val
            if max_val:
                attr.max_value = max_val

            depends_id = data.get('depends_on_choice', '').strip()
            if depends_id:
                attr.depends_on_choice = get_object_or_404(AttributeChoice, pk=depends_id)

            attr.save()
            messages.success(request, f'Attribut « {attr.label_fr} » créé.')
        except Exception as e:
            messages.error(request, str(e))

        return redirect('adminpanel:attribute-list', cat_pk=cat_pk)

    def _get_available_choices(self, category):
        cat_ids = [category.pk]
        if category.parent:
            cat_ids.append(category.parent.pk)
        return AttributeChoice.objects.filter(
            attribute__category_id__in=cat_ids,
            attribute__attribute_type__in=['CHOICE', 'MULTI_CHOICE'],
        ).select_related('attribute').order_by('attribute__name', 'order')


class AttributeEditView(StaffRequiredMixin, View):
    def get(self, request, pk):
        attr = get_object_or_404(AttributeDefinition, pk=pk)
        available_choices = self._get_available_choices(attr.category)
        return render(request, 'adminpanel/attributes/form.html', {
            'category': attr.category,
            'attribute': attr,
            'available_choices': available_choices,
            'title': f'Modifier « {attr.label_fr} »',
        })

    def post(self, request, pk):
        attr = get_object_or_404(AttributeDefinition, pk=pk)
        data = request.POST
        try:
            attr.name = data.get('name', '').strip()
            attr.label_fr = data.get('label_fr', '').strip()
            attr.attribute_type = data.get('attribute_type', attr.attribute_type)
            attr.required = data.get('required') == 'on'
            attr.filterable = data.get('filterable') == 'on'
            attr.order = int(data.get('order', 0))
            attr.unit = data.get('unit', '').strip()

            min_val = data.get('min_value', '').strip()
            max_val = data.get('max_value', '').strip()
            attr.min_value = min_val if min_val else None
            attr.max_value = max_val if max_val else None

            depends_id = data.get('depends_on_choice', '').strip()
            attr.depends_on_choice = get_object_or_404(AttributeChoice, pk=depends_id) if depends_id else None

            attr.save()
            messages.success(request, f'Attribut « {attr.label_fr} » modifié.')
        except Exception as e:
            messages.error(request, str(e))

        return redirect('adminpanel:attribute-list', cat_pk=attr.category.pk)

    def _get_available_choices(self, category):
        cat_ids = [category.pk]
        if category.parent:
            cat_ids.append(category.parent.pk)
        return AttributeChoice.objects.filter(
            attribute__category_id__in=cat_ids,
            attribute__attribute_type__in=['CHOICE', 'MULTI_CHOICE'],
        ).select_related('attribute').order_by('attribute__name', 'order')


class AttributeDeleteView(StaffRequiredMixin, View):
    def post(self, request, pk):
        attr = get_object_or_404(AttributeDefinition, pk=pk)
        cat_pk = attr.category.pk
        name = attr.label_fr
        attr.delete()
        messages.success(request, f'Attribut « {name} » supprimé.')
        return redirect('adminpanel:attribute-list', cat_pk=cat_pk)


# ──────────────────────── Choices CRUD ────────────────────────


class ChoiceListView(StaffRequiredMixin, View):
    def get(self, request, attr_pk):
        attr = get_object_or_404(AttributeDefinition, pk=attr_pk)
        choices = attr.choices.order_by('order')
        return render(request, 'adminpanel/choices/list.html', {
            'attribute': attr,
            'choices': choices,
        })


class ChoiceCreateView(StaffRequiredMixin, View):
    def get(self, request, attr_pk):
        attr = get_object_or_404(AttributeDefinition, pk=attr_pk)
        return render(request, 'adminpanel/choices/form.html', {
            'attribute': attr,
            'title': f'Ajouter un choix à « {attr.label_fr} »',
        })

    def post(self, request, attr_pk):
        attr = get_object_or_404(AttributeDefinition, pk=attr_pk)
        value = request.POST.get('value', '').strip()
        order = request.POST.get('order', '0').strip()

        if not value:
            messages.error(request, 'La valeur est obligatoire.')
            return redirect('adminpanel:choice-create', attr_pk=attr_pk)

        try:
            AttributeChoice.objects.create(
                attribute=attr,
                value=value,
                order=int(order) if order else 0,
            )
            messages.success(request, f'Choix « {value} » ajouté.')
        except Exception as e:
            messages.error(request, str(e))

        return redirect('adminpanel:choice-list', attr_pk=attr_pk)


class ChoiceEditView(StaffRequiredMixin, View):
    def get(self, request, pk):
        choice = get_object_or_404(AttributeChoice, pk=pk)
        return render(request, 'adminpanel/choices/form.html', {
            'attribute': choice.attribute,
            'choice': choice,
            'title': f'Modifier « {choice.value} »',
        })

    def post(self, request, pk):
        choice = get_object_or_404(AttributeChoice, pk=pk)
        value = request.POST.get('value', '').strip()
        order = request.POST.get('order', '0').strip()

        if not value:
            messages.error(request, 'La valeur est obligatoire.')
            return redirect('adminpanel:choice-edit', pk=pk)

        choice.value = value
        choice.order = int(order) if order else 0
        choice.save()
        messages.success(request, 'Choix modifié.')
        return redirect('adminpanel:choice-list', attr_pk=choice.attribute.pk)


class ChoiceDeleteView(StaffRequiredMixin, View):
    def post(self, request, pk):
        choice = get_object_or_404(AttributeChoice, pk=pk)
        attr_pk = choice.attribute.pk
        choice.delete()
        messages.success(request, 'Choix supprimé.')
        return redirect('adminpanel:choice-list', attr_pk=attr_pk)


# ──────────────────────── Reorder (AJAX) ────────────────────────


class CategoryReorderView(StaffRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            items = data.get('items', [])
            for item in items:
                Category.objects.filter(pk=item['id']).update(order=item['order'])
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


class AttributeReorderView(StaffRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            items = data.get('items', [])
            for item in items:
                AttributeDefinition.objects.filter(pk=item['id']).update(order=item['order'])
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


class ChoiceReorderView(StaffRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            items = data.get('items', [])
            for item in items:
                AttributeChoice.objects.filter(pk=item['id']).update(order=item['order'])
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


# ──────────────────────── AI Generation ────────────────────────


class AIGenerateView(StaffRequiredMixin, View):
    def get(self, request):
        return render(request, 'adminpanel/ai/generate.html')

    def post(self, request):
        from adminpanel.services import generate_catalog_from_ai

        product_type = request.POST.get('product_type', '').strip()
        if not product_type:
            messages.error(request, 'Décrivez le type de produit.')
            return redirect('adminpanel:ai-generate')

        try:
            result = generate_catalog_from_ai(product_type)
            request.session['ai_catalog_result'] = result
            return render(request, 'adminpanel/ai/preview.html', {
                'product_type': product_type,
                'result': result,
            })
        except Exception as e:
            messages.error(request, f'Erreur AI : {e}')
            return redirect('adminpanel:ai-generate')


class AIGenerateConfirmView(StaffRequiredMixin, View):
    def post(self, request):
        from adminpanel.services import save_ai_catalog_result

        result = request.session.get('ai_catalog_result')
        if not result:
            messages.error(request, 'Aucune génération en attente.')
            return redirect('adminpanel:ai-generate')

        try:
            save_ai_catalog_result(result)
            del request.session['ai_catalog_result']
            messages.success(request, 'Catalogue généré et sauvegardé avec succès !')
        except Exception as e:
            messages.error(request, f'Erreur lors de la sauvegarde : {e}')

        return redirect('adminpanel:category-list')
