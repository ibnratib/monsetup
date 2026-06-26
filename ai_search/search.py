from django.db.models import Q

from catalog.models import AttributeDefinition, Category
from core.models import City
from products.models import Product


def execute_search(filters: dict):
    """
    Execute a product search based on AI-extracted filters.

    Args:
        filters: dict with optional keys:
            - category_slug: str
            - price_min: number
            - price_max: number
            - ville: str
            - keywords: str
            - attributes: dict of {attr_name: value}

    Returns:
        QuerySet of matching products.
    """
    qs = Product.objects.filter(status='DISPONIBLE').select_related(
        'category', 'category__parent', 'ville', 'seller'
    ).prefetch_related('images')

    # Category filter
    category_slug = filters.get('category_slug')
    if category_slug:
        try:
            category = Category.objects.get(slug=category_slug)
            # If it's a parent category, include all children
            if category.parent is None:
                child_ids = category.children.values_list('id', flat=True)
                qs = qs.filter(Q(category=category) | Q(category_id__in=child_ids))
            else:
                qs = qs.filter(category=category)
        except Category.DoesNotExist:
            pass

    # Price filters
    price_min = filters.get('price_min')
    if price_min is not None:
        qs = qs.filter(price__gte=price_min)

    price_max = filters.get('price_max')
    if price_max is not None:
        qs = qs.filter(price__lte=price_max)

    # City filter
    ville = filters.get('ville')
    if ville:
        try:
            city = City.objects.get(name__iexact=ville)
            qs = qs.filter(ville=city)
        except City.DoesNotExist:
            # Try partial match
            cities = City.objects.filter(name__icontains=ville)
            if cities.exists():
                qs = qs.filter(ville__in=cities)

    # Keyword search in title and description
    keywords = filters.get('keywords')
    if keywords:
        words = keywords.split()
        q = Q()
        for word in words:
            q &= (
                Q(title__icontains=word) |
                Q(description_complementaire__icontains=word)
            )
        qs = qs.filter(q)

    # EAV attribute filters
    attributes = filters.get('attributes', {})
    for attr_name, value in attributes.items():
        attr_defs = AttributeDefinition.objects.filter(
            name__iexact=attr_name, filterable=True
        )
        if not attr_defs.exists():
            continue

        for attr_def in attr_defs:
            attr_type = attr_def.attribute_type
            filter_kwargs = {'attribute_values__attribute': attr_def}

            if attr_type == 'INT':
                try:
                    filter_kwargs['attribute_values__value_int'] = int(value)
                except (ValueError, TypeError):
                    continue
            elif attr_type == 'DECIMAL':
                try:
                    filter_kwargs['attribute_values__value_decimal'] = float(value)
                except (ValueError, TypeError):
                    continue
            elif attr_type == 'BOOLEAN':
                filter_kwargs['attribute_values__value_boolean'] = str(value).lower() in ('true', '1', 'oui')
            elif attr_type in ('CHOICE', 'MULTI_CHOICE'):
                filter_kwargs['attribute_values__value_choice__value__iexact'] = str(value)
            elif attr_type == 'TEXT_SHORT':
                filter_kwargs['attribute_values__value_text__icontains'] = str(value)
            else:
                continue

            qs = qs.filter(**filter_kwargs)
            break  # Use first matching attribute definition

    # Order: boosted first, then newest
    qs = qs.order_by('-is_boosted', '-created_at')

    return qs
