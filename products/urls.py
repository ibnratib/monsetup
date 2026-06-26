from django.urls import path

from products.views import (
    FavoriteDeleteAPIView,
    FavoriteListCreateAPIView,
    ProductCreateView,
    ProductDetailAPIView,
    ProductDetailView,
    ProductListCreateAPIView,
    ProductListView,
    ProductReportAPIView,
    ProductTrackWhatsAppAPIView,
)

# API endpoints
api_urlpatterns = [
    path('', ProductListCreateAPIView.as_view(), name='product-list-create'),
    path('<int:pk>/', ProductDetailAPIView.as_view(), name='product-detail-api'),
    path('<int:pk>/report/', ProductReportAPIView.as_view(), name='product-report'),
    path('<int:pk>/track-whatsapp/', ProductTrackWhatsAppAPIView.as_view(), name='product-track-whatsapp'),
]

# Favorites API
favorites_api_urlpatterns = [
    path('', FavoriteListCreateAPIView.as_view(), name='favorite-list-create'),
    path('<int:pk>/', FavoriteDeleteAPIView.as_view(), name='favorite-delete'),
]

# SSR endpoints
ssr_urlpatterns = [
    path('', ProductListView.as_view(), name='product-list'),
    path('deposer/', ProductCreateView.as_view(), name='product-create'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
]
