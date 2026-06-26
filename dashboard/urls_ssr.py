from django.urls import path

from dashboard.views import DashboardHomeView, FavoritesView, MyProductsView, NotificationsView

urlpatterns = [
    path('', DashboardHomeView.as_view(), name='dashboard-home'),
    path('mes-annonces/', MyProductsView.as_view(), name='dashboard-my-products-ssr'),
    path('notifications/', NotificationsView.as_view(), name='dashboard-notifications-ssr'),
    path('favoris/', FavoritesView.as_view(), name='dashboard-favorites-ssr'),
]
