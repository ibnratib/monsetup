from django.urls import path

from reviews.views import (
    ReviewReplyAPIView,
    ReviewReportAPIView,
    ReviewTagListAPIView,
    SellerReviewListCreateAPIView,
)

urlpatterns = [
    path('sellers/<int:seller_id>/reviews/', SellerReviewListCreateAPIView.as_view(), name='seller-reviews'),
    path('reviews/<int:pk>/reply/', ReviewReplyAPIView.as_view(), name='review-reply'),
    path('reviews/<int:pk>/report/', ReviewReportAPIView.as_view(), name='review-report'),
    path('review-tags/', ReviewTagListAPIView.as_view(), name='review-tag-list'),
]
