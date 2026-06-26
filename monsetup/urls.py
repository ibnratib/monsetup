"""
URL configuration for monsetup project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from accounts.views import BoutiquePageView, LoginSSRView, LogoutSSRView
from catalog.views import CityListView
from core.views import HomePageView
from products.urls import api_urlpatterns as products_api, favorites_api_urlpatterns as favorites_api, ssr_urlpatterns as products_ssr
from ai_search.urls import api_urlpatterns as ai_search_api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin-panel/', include('adminpanel.urls')),
    path('api/v1/auth/', include('accounts.urls')),
    path('api/v1/catalog/', include('catalog.urls')),
    path('api/v1/cities/', CityListView.as_view(), name='city-list'),
    path('api/v1/products/', include(products_api)),
    path('api/v1/favorites/', include(favorites_api)),
    path('api/v1/dashboard/', include('dashboard.urls_api')),
    path('api/v1/', include('reviews.urls_api')),
    path('api/v1/ai-search/', include(ai_search_api)),
    path('inscription/', include('accounts.urls_ssr')),
    path('connexion/', LoginSSRView.as_view(), name='login'),
    path('deconnexion/', LogoutSSRView.as_view(), name='logout'),
    path('annonces/', include(products_ssr)),
    path('dashboard/', include('dashboard.urls_ssr')),
    path('vendeur/', include('reviews.urls_ssr')),
    path('boutique/<slug:slug>/', BoutiquePageView.as_view(), name='boutique-page'),
    path('', HomePageView.as_view(), name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
