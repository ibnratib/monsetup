from django.urls import path

from dashboard.views import (
    DashboardStatsAPIView,
    MyProductListAPIView,
    NotificationListAPIView,
    NotificationMarkAllReadAPIView,
    NotificationMarkReadAPIView,
    ProductStatusUpdateAPIView,
)

urlpatterns = [
    path('my-products/', MyProductListAPIView.as_view(), name='dashboard-my-products'),
    path('my-products/<int:pk>/status/', ProductStatusUpdateAPIView.as_view(), name='dashboard-product-status'),
    path('stats/', DashboardStatsAPIView.as_view(), name='dashboard-stats'),
    path('notifications/', NotificationListAPIView.as_view(), name='dashboard-notifications'),
    path('notifications/<int:pk>/read/', NotificationMarkReadAPIView.as_view(), name='dashboard-notification-read'),
    path('notifications/mark-all-read/', NotificationMarkAllReadAPIView.as_view(), name='dashboard-notifications-mark-all-read'),
]
