from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, TemplateView

from dashboard.models import Notification
from dashboard.permissions import IsNotificationOwner
from dashboard.serializers import (
    DashboardStatsSerializer,
    MyProductListSerializer,
    NotificationSerializer,
    ProductStatusUpdateSerializer,
)
from products.models import Favorite, Product


# ──────────────────────── API Views ────────────────────────


class MyProductListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = Product.objects.filter(
            seller=request.user,
        ).select_related('ville', 'category').prefetch_related('images')

        # Filtrage optionnel par statut
        status_filter = request.query_params.get('status', '').strip()
        if status_filter in ('DISPONIBLE', 'VENDU', 'ARCHIVE'):
            queryset = queryset.filter(status=status_filter)

        queryset = queryset.order_by('-created_at')

        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = MyProductListSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)


class ProductStatusUpdateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        product = get_object_or_404(Product, pk=pk, seller=request.user)
        serializer = ProductStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product.status = serializer.validated_data['status']
        product.save(update_fields=['status', 'updated_at'])
        return Response({'data': {'id': product.id, 'status': product.status}})


class DashboardStatsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        products = Product.objects.filter(seller=request.user)
        aggregates = products.aggregate(
            total_views=Sum('views_count'),
            total_whatsapp_clicks=Sum('whatsapp_clicks_count'),
        )
        data = {
            'total_products': products.count(),
            'total_views': aggregates['total_views'] or 0,
            'total_whatsapp_clicks': aggregates['total_whatsapp_clicks'] or 0,
            'products_disponible': products.filter(status='DISPONIBLE').count(),
            'products_vendu': products.filter(status='VENDU').count(),
            'products_archive': products.filter(status='ARCHIVE').count(),
        }
        serializer = DashboardStatsSerializer(data)
        return Response({'data': serializer.data})


class NotificationListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = Notification.objects.filter(
            user=request.user,
        ).select_related('product').order_by('-created_at')

        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = NotificationSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class NotificationMarkReadAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsNotificationOwner]

    def patch(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk)
        self.check_object_permissions(request, notification)
        notification.is_read = True
        notification.save(update_fields=['is_read', 'updated_at'])
        return Response({'data': {'id': notification.id, 'is_read': True}})


class NotificationMarkAllReadAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        updated = Notification.objects.filter(
            user=request.user, is_read=False,
        ).update(is_read=True)
        return Response({'data': {'marked_read': updated}})


# ──────────────────────── SSR Views ────────────────────────


class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard_home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        products = Product.objects.filter(seller=user)
        aggregates = products.aggregate(
            total_views=Sum('views_count'),
            total_whatsapp_clicks=Sum('whatsapp_clicks_count'),
        )
        context['stats'] = {
            'total_products': products.count(),
            'total_views': aggregates['total_views'] or 0,
            'total_whatsapp_clicks': aggregates['total_whatsapp_clicks'] or 0,
            'products_disponible': products.filter(status='DISPONIBLE').count(),
        }
        context['recent_products'] = products.select_related(
            'ville', 'category',
        ).prefetch_related('images').order_by('-created_at')[:5]
        context['unread_notifications'] = Notification.objects.filter(
            user=user, is_read=False,
        ).select_related('product').order_by('-created_at')[:5]
        context['unread_count'] = Notification.objects.filter(
            user=user, is_read=False,
        ).count()
        return context


class MyProductsView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/my_products.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        queryset = Product.objects.filter(
            seller=self.request.user,
        ).select_related('ville', 'category').prefetch_related('images').order_by('-created_at')

        status_filter = self.request.GET.get('status', '').strip()
        if status_filter in ('DISPONIBLE', 'VENDU', 'ARCHIVE'):
            queryset = queryset.filter(status=status_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_status'] = self.request.GET.get('status', '')
        context['unread_count'] = Notification.objects.filter(
            user=self.request.user, is_read=False,
        ).count()
        return context

    def post(self, request):
        """Handle status change via POST form."""
        product_id = request.POST.get('product_id')
        new_status = request.POST.get('status')
        if product_id and new_status in ('DISPONIBLE', 'VENDU', 'ARCHIVE'):
            Product.objects.filter(
                pk=product_id, seller=request.user,
            ).update(status=new_status)
        from django.shortcuts import redirect
        return redirect(request.get_full_path())


class NotificationsView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user,
        ).select_related('product').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_count'] = Notification.objects.filter(
            user=self.request.user, is_read=False,
        ).count()
        return context

    def post(self, request):
        """Handle mark-as-read and mark-all-read via POST form."""
        action = request.POST.get('action')
        if action == 'mark_read':
            notif_id = request.POST.get('notification_id')
            if notif_id:
                Notification.objects.filter(
                    pk=notif_id, user=request.user,
                ).update(is_read=True)
        elif action == 'mark_all_read':
            Notification.objects.filter(
                user=request.user, is_read=False,
            ).update(is_read=True)
        from django.shortcuts import redirect
        return redirect(request.get_full_path())


class FavoritesView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/favorites.html'
    context_object_name = 'favorites'
    paginate_by = 20

    def get_queryset(self):
        return Favorite.objects.filter(
            user=self.request.user,
        ).select_related(
            'product', 'product__ville',
        ).prefetch_related('product__images').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_count'] = Notification.objects.filter(
            user=self.request.user, is_read=False,
        ).count()
        return context

    def post(self, request):
        """Handle remove favorite via POST."""
        favorite_id = request.POST.get('favorite_id')
        if favorite_id:
            Favorite.objects.filter(pk=favorite_id, user=request.user).delete()
        from django.shortcuts import redirect
        return redirect(request.get_full_path())
