from django.contrib.auth import get_user_model
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView
from rest_framework import permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product
from reviews.models import Review, ReviewTag
from reviews.permissions import IsReviewedSeller
from reviews.serializers import (
    ReviewCreateSerializer,
    ReviewReplyCreateSerializer,
    ReviewReportSerializer,
    ReviewSerializer,
    ReviewTagSerializer,
)

User = get_user_model()


# ──────────────────────── API Views ────────────────────────


class SellerReviewListCreateAPIView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get(self, request, seller_id):
        seller = get_object_or_404(User, pk=seller_id)
        queryset = Review.objects.filter(
            seller=seller,
        ).select_related(
            'reviewer',
        ).prefetch_related(
            'tags', 'reply',
        ).order_by('-created_at')

        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = ReviewSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, seller_id):
        seller = get_object_or_404(User, pk=seller_id)
        serializer = ReviewCreateSerializer(
            data=request.data,
            context={'request': request, 'seller': seller},
        )
        serializer.is_valid(raise_exception=True)
        review = serializer.save()
        detail_serializer = ReviewSerializer(review)
        return Response({'data': detail_serializer.data}, status=status.HTTP_201_CREATED)


class ReviewReplyAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        review = get_object_or_404(
            Review.objects.select_related('reviewer'),
            pk=pk,
        )
        serializer = ReviewReplyCreateSerializer(
            data=request.data,
            context={'request': request, 'review': review},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        detail_serializer = ReviewSerializer(review)
        return Response({'data': detail_serializer.data}, status=status.HTTP_201_CREATED)


class ReviewReportAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        review = get_object_or_404(Review, pk=pk)
        serializer = ReviewReportSerializer(
            data=request.data,
            context={'request': request, 'review': review},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'data': {'message': 'Votre signalement a été envoyé.'}},
            status=status.HTTP_201_CREATED,
        )


class ReviewTagListAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        tags = ReviewTag.objects.all()
        serializer = ReviewTagSerializer(tags, many=True)
        return Response({'data': serializer.data})


# ──────────────────────── Helpers ────────────────────────


def _get_seller_context(seller):
    """Build seller review summary context."""
    reviews = Review.objects.filter(seller=seller)
    stats = reviews.aggregate(
        average_rating=Avg('rating'),
        reviews_count=Count('id'),
    )
    average_rating = round(stats['average_rating'], 1) if stats['average_rating'] else None
    reviews_count = stats['reviews_count']

    # Top 3 tags
    top_tags = (
        ReviewTag.objects.filter(reviews__seller=seller)
        .annotate(tag_count=Count('id'))
        .order_by('-tag_count')[:3]
    )

    return {
        'average_rating': average_rating,
        'reviews_count': reviews_count,
        'top_tags': top_tags,
    }


# ──────────────────────── SSR Views ────────────────────────


class SellerProfileView(DetailView):
    model = User
    template_name = 'reviews/seller_profile.html'
    context_object_name = 'seller'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        seller = self.object

        # Review summary
        context.update(_get_seller_context(seller))

        # Last 5 reviews
        context['reviews'] = (
            Review.objects.filter(seller=seller)
            .select_related('reviewer')
            .prefetch_related('tags', 'reply')
            .order_by('-created_at')[:5]
        )

        # Seller's last 4 active products
        context['products'] = (
            Product.objects.filter(seller=seller, status='DISPONIBLE')
            .select_related('ville')
            .prefetch_related('images')
            .order_by('-created_at')[:4]
        )

        # Available tags for review form
        context['review_tags'] = ReviewTag.objects.all()

        # Check if current user already reviewed this seller
        if self.request.user.is_authenticated:
            existing_review = Review.objects.filter(
                reviewer=self.request.user, seller=seller,
            ).prefetch_related('tags').first()
            context['existing_review'] = existing_review

        # Seller profile info
        context['is_boutique'] = seller.user_type == 'boutique'
        if context['is_boutique']:
            try:
                context['boutique'] = seller.boutique
            except Exception:
                context['boutique'] = None

        return context


class SellerReviewsView(ListView):
    template_name = 'reviews/seller_reviews.html'
    context_object_name = 'reviews'
    paginate_by = 20

    def get_queryset(self):
        self.seller = get_object_or_404(User, pk=self.kwargs['pk'])
        return (
            Review.objects.filter(seller=self.seller)
            .select_related('reviewer')
            .prefetch_related('tags', 'reply')
            .order_by('-created_at')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seller'] = self.seller
        context.update(_get_seller_context(self.seller))
        return context
