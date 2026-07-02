import django_filters

from products.models import Product


class ProductFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name='category__slug', lookup_expr='exact')
    category_root = django_filters.CharFilter(field_name='category__parent__slug', lookup_expr='exact')
    ville = django_filters.NumberFilter(field_name='ville__id', lookup_expr='exact')
    status = django_filters.CharFilter(field_name='status', lookup_expr='exact')
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    seller_type = django_filters.CharFilter(field_name='seller__user_type', lookup_expr='exact')
    condition = django_filters.CharFilter(field_name='condition', lookup_expr='exact')
    is_boosted = django_filters.BooleanFilter(field_name='is_boosted')

    class Meta:
        model = Product
        fields = []
