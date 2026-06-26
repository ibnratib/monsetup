from django.urls import path

from catalog.views import (
    CategoryAttributesByIdView,
    CategoryAttributesView,
    CategoryDetailView,
    CategoryListView,
    FilterableAttributesView,
)

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category-detail'),
    path('categories/<slug:slug>/attributes/', CategoryAttributesView.as_view(), name='category-attributes'),
    path('categories/<slug:slug>/filterable-attributes/', FilterableAttributesView.as_view(), name='category-filterable-attributes'),
    path('categories/<int:pk>/attributes-by-id/', CategoryAttributesByIdView.as_view(), name='category-attributes-by-id'),
]
