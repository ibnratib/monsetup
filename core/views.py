from django.utils import timezone
from django.views.generic import TemplateView

from catalog.models import Category
from products.models import Product


class HomePageView(TemplateView):
    template_name = 'pages/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()

        context['boosted_products'] = (
            Product.objects.filter(
                is_boosted=True,
                boost_expires_at__gt=now,
                status='DISPONIBLE',
            )
            .select_related('ville', 'category')
            .prefetch_related('images')[:8]
        )

        context['latest_products'] = (
            Product.objects.filter(status='DISPONIBLE')
            .order_by('-created_at')
            .select_related('ville', 'category')
            .prefetch_related('images')[:8]
        )

        context['root_categories'] = Category.objects.filter(
            parent__isnull=True,
        ).order_by('order')

        return context
