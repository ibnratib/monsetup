from django.urls import path

from accounts.views import RegisterBoutiqueSSRView, RegisterChoiceView, RegisterParticulierSSRView

urlpatterns = [
    path('', RegisterChoiceView.as_view(), name='register-choice'),
    path('particulier/', RegisterParticulierSSRView.as_view(), name='register-particulier-ssr'),
    path('boutique/', RegisterBoutiqueSSRView.as_view(), name='register-boutique-ssr'),
]
