from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.views import MeView, RegisterBoutiqueView, RegisterParticulierView

urlpatterns = [
    path('register/particulier/', RegisterParticulierView.as_view(), name='register-particulier'),
    path('register/boutique/', RegisterBoutiqueView.as_view(), name='register-boutique'),
    path('token/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('me/', MeView.as_view(), name='me'),
]
