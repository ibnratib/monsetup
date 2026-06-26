from rest_framework import generics
from rest_framework.response import Response

from catalog.models import Category
from catalog.serializers import (
    AttributeDefinitionSerializer,
    CategoryDetailSerializer,
    CategoryListSerializer,
    CitySerializer,
    FilterableAttributeSerializer,
)
from core.models import City


class CategoryListView(generics.ListAPIView):
    """Liste des catégories racines avec sous-catégories imbriquées."""
    serializer_class = CategoryListSerializer

    def get_queryset(self):
        return Category.objects.filter(parent__isnull=True).prefetch_related('children')


class CategoryDetailView(generics.RetrieveAPIView):
    """Détail d'une catégorie avec ses attributs hérités."""
    serializer_class = CategoryDetailSerializer
    lookup_field = 'slug'
    queryset = Category.objects.all()


class CategoryAttributesView(generics.ListAPIView):
    """Liste des attributs (avec héritage) d'une catégorie."""
    serializer_class = AttributeDefinitionSerializer

    def list(self, request, *args, **kwargs):
        slug = self.kwargs['slug']
        category = generics.get_object_or_404(Category, slug=slug)
        attributes = category.get_inherited_attributes()
        serializer = AttributeDefinitionSerializer(attributes, many=True)
        return Response(serializer.data)


class CategoryAttributesByIdView(generics.ListAPIView):
    """Liste des attributs d'une catégorie par ID (pour le formulaire SSR)."""
    serializer_class = AttributeDefinitionSerializer

    def list(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        category = generics.get_object_or_404(Category, pk=pk)
        attributes = category.get_inherited_attributes()
        serializer = AttributeDefinitionSerializer(attributes, many=True)
        return Response({'data': serializer.data})


class CityListView(generics.ListAPIView):
    """Liste des villes triées par nom."""
    serializer_class = CitySerializer
    queryset = City.objects.all()
    pagination_class = None


class FilterableAttributesView(generics.ListAPIView):
    """Attributs filtrables d'une catégorie (avec choices) pour construire le formulaire de filtres."""
    serializer_class = FilterableAttributeSerializer

    def list(self, request, *args, **kwargs):
        slug = self.kwargs['slug']
        category = generics.get_object_or_404(Category, slug=slug)
        attributes = [
            attr for attr in category.get_inherited_attributes() if attr.filterable
        ]
        serializer = FilterableAttributeSerializer(attributes, many=True)
        return Response({'data': serializer.data})
