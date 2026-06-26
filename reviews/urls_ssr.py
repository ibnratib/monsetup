from django.urls import path

from reviews.views import SellerProfileView, SellerReviewsView

urlpatterns = [
    path('<int:pk>/', SellerProfileView.as_view(), name='seller-profile'),
    path('<int:pk>/avis/', SellerReviewsView.as_view(), name='seller-reviews-page'),
]
