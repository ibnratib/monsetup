from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Boutique, Particulier
from accounts.serializers import (
    MeUpdateSerializer,
    ProfileSerializer,
    RegisterBoutiqueSerializer,
    RegisterParticulierSerializer,
)
from core.models import City


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RegisterParticulierView(generics.CreateAPIView):
    serializer_class = RegisterParticulierSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = get_tokens_for_user(user)
        profile_data = ProfileSerializer(user).data
        return Response(
            {'data': {'user': profile_data, 'tokens': tokens}},
            status=status.HTTP_201_CREATED,
        )


class RegisterBoutiqueView(generics.CreateAPIView):
    serializer_class = RegisterBoutiqueSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = get_tokens_for_user(user)
        profile_data = ProfileSerializer(user).data
        return Response(
            {'data': {'user': profile_data, 'tokens': tokens}},
            status=status.HTTP_201_CREATED,
        )


class MeView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        data = ProfileSerializer(user).data
        return Response({'data': data})

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = MeUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Update boutique-specific fields if applicable
        if user.user_type == 'boutique' and hasattr(user, 'boutique'):
            boutique_fields = {'nom_boutique', 'description', 'adresse'}
            boutique_data = {k: v for k, v in request.data.items() if k in boutique_fields}
            if boutique_data:
                for field, value in boutique_data.items():
                    setattr(user.boutique, field, value)
                user.boutique.save()

        data = ProfileSerializer(user).data
        return Response({'data': data})

    def put(self, request, *args, **kwargs):
        return self.patch(request, *args, **kwargs)


# ──────────────────────── SSR Views ────────────────────────


class RegisterChoiceView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard-home')
        return render(request, 'accounts/register_choice.html')


class RegisterParticulierSSRView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard-home')
        return render(request, 'accounts/register_particulier.html')

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard-home')

        data = {
            'email': request.POST.get('email', ''),
            'password': request.POST.get('password', ''),
            'first_name': request.POST.get('first_name', ''),
            'last_name': request.POST.get('last_name', ''),
            'phone_whatsapp': request.POST.get('phone_whatsapp', ''),
        }
        serializer = RegisterParticulierSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('dashboard-home')

        return render(request, 'accounts/register_particulier.html', {
            'errors': serializer.errors,
            'form_data': request.POST,
        })


class RegisterBoutiqueSSRView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard-home')
        cities = City.objects.all()
        return render(request, 'accounts/register_boutique.html', {'cities': cities})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard-home')

        data = {
            'email': request.POST.get('email', ''),
            'password': request.POST.get('password', ''),
            'nom_boutique': request.POST.get('nom_boutique', ''),
            'phone_whatsapp': request.POST.get('phone_whatsapp', ''),
            'adresse': request.POST.get('adresse', ''),
            'ville': request.POST.get('ville', ''),
        }
        serializer = RegisterBoutiqueSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('dashboard-home')

        cities = City.objects.all()
        return render(request, 'accounts/register_boutique.html', {
            'errors': serializer.errors,
            'form_data': request.POST,
            'cities': cities,
        })


class LoginSSRView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard-home')
        return render(request, 'accounts/login.html')

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard-home')

        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next') or request.POST.get('next') or ''
            if next_url:
                return redirect(next_url)
            if user.is_staff:
                return redirect('adminpanel:dashboard')
            return redirect('dashboard-home')

        return render(request, 'accounts/login.html', {
            'errors': {'non_field_errors': ['Email ou mot de passe incorrect.']},
            'form_data': request.POST,
        })


class LogoutSSRView(View):
    def get(self, request):
        logout(request)
        return redirect('product-list')

    def post(self, request):
        logout(request)
        return redirect('product-list')


class BoutiquePageView(View):
    def get(self, request, slug):
        boutique = get_object_or_404(
            Boutique.objects.select_related('user', 'ville'),
            slug=slug,
        )

        products = (
            boutique.user.products
            .filter(status='DISPONIBLE')
            .select_related('ville', 'category')
            .prefetch_related('images')
            .order_by('-created_at')
        )
        paginator = Paginator(products, 20)
        page_obj = paginator.get_page(request.GET.get('page'))

        reviews = (
            boutique.user.received_reviews
            .select_related('reviewer')
            .order_by('-created_at')[:5]
        )

        review_stats = boutique.user.received_reviews.aggregate(avg_rating=Avg('rating'))
        avg_rating = review_stats['avg_rating']
        review_count = boutique.user.received_reviews.count()

        return render(request, 'accounts/boutique_page.html', {
            'boutique': boutique,
            'page_obj': page_obj,
            'reviews': reviews,
            'avg_rating': avg_rating,
            'review_count': review_count,
        })
