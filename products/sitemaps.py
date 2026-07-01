from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from accounts.models import Boutique
from catalog.models import Category
from core.models import City
from products.models import Product


class StaticSitemap(Sitemap):
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        return ['home', 'product-list']

    def location(self, item):
        return reverse(item)


class ProductSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.8

    def items(self):
        return Product.objects.filter(status='DISPONIBLE').select_related('ville', 'category')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class CategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Category.objects.filter(parent__isnull=False)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('product-list') + f'?category={obj.slug}'


class CitySitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.7

    def items(self):
        return City.objects.filter(
            products__status='DISPONIBLE',
        ).distinct()

    def location(self, obj):
        return reverse('product-list-by-city', kwargs={'city_slug': obj.slug})


class BoutiqueSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return Boutique.objects.filter(
            statut_verification='VERIFIE',
        ).select_related('ville')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('boutique-page', kwargs={'slug': obj.slug})


class CityCategorySitemap(Sitemap):
    """Cross-product of active cities x subcategories for local SEO landing pages."""
    changefreq = 'daily'
    priority = 0.7

    def items(self):
        cities = City.objects.filter(
            products__status='DISPONIBLE',
        ).distinct()
        subcategories = Category.objects.filter(
            parent__isnull=False,
            products__status='DISPONIBLE',
        ).distinct()

        combinations = []
        for city in cities:
            for cat in subcategories:
                combinations.append((city.slug, cat.slug))
        return combinations

    def location(self, item):
        return reverse(
            'product-list-by-city-category',
            kwargs={'city_slug': item[0], 'category_slug': item[1]},
        )
