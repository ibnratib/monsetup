from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, F, IntegerField, Q, Value, When
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.text import slugify
from django.views import View
from django.views.generic import DetailView, ListView
from rest_framework import permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from catalog.models import AttributeDefinition, Category
from core.models import City
from products.filters import ProductFilter
from products.models import Favorite, Product, ProductView as ProductViewModel, ProductWhatsAppClick
from products.permissions import IsProductOwner
from products.serializers import (
    DynamicProductCreateSerializer,
    FavoriteCreateSerializer,
    FavoriteSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    ReportCreateSerializer,
)


def _apply_eav_filters(queryset, query_params):
    """Apply dynamic EAV attribute filters from query params like attr_<id>=<value>."""
    for key, value in query_params.items():
        if not key.startswith('attr_'):
            continue
        try:
            attr_id = int(key[5:])
        except (ValueError, TypeError):
            continue
        try:
            attr_def = AttributeDefinition.objects.get(pk=attr_id, filterable=True)
        except AttributeDefinition.DoesNotExist:
            continue

        attr_type = attr_def.attribute_type
        filter_kwargs = {'attribute_values__attribute': attr_def}

        if attr_type == 'INT':
            try:
                filter_kwargs['attribute_values__value_int'] = int(value)
            except (ValueError, TypeError):
                continue
        elif attr_type == 'DECIMAL':
            try:
                filter_kwargs['attribute_values__value_decimal'] = value
            except (ValueError, TypeError):
                continue
        elif attr_type == 'BOOLEAN':
            bool_val = value.lower() in ('true', '1', 'yes')
            filter_kwargs['attribute_values__value_boolean'] = bool_val
        elif attr_type == 'CHOICE':
            try:
                filter_kwargs['attribute_values__value_choice_id'] = int(value)
            except (ValueError, TypeError):
                continue
        elif attr_type == 'MULTI_CHOICE':
            try:
                filter_kwargs['attribute_values__value_multi_choice__id'] = int(value)
            except (ValueError, TypeError):
                continue
        elif attr_type == 'TEXT_SHORT':
            filter_kwargs['attribute_values__value_text__icontains'] = value
        else:
            continue

        queryset = queryset.filter(**filter_kwargs)
    return queryset


def _apply_boost_ordering(queryset, ordering_param):
    """Boosted products first, then apply user ordering."""
    now = timezone.now()
    queryset = queryset.annotate(
        is_currently_boosted=Case(
            When(is_boosted=True, boost_expires_at__gt=now, then=Value(0)),
            default=Value(1),
            output_field=IntegerField(),
        ),
    )
    valid_fields = {'created_at', '-created_at', 'price', '-price'}
    if ordering_param and ordering_param in valid_fields:
        return queryset.order_by('is_currently_boosted', ordering_param)
    return queryset.order_by('is_currently_boosted', '-created_at')


# ──────────────────────── API Views ────────────────────────


class ProductListCreateAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get(self, request):
        queryset = Product.objects.select_related(
            'ville', 'category', 'category__parent', 'seller',
        ).prefetch_related('images')

        # Default: only DISPONIBLE for public listing
        if 'status' not in request.query_params:
            queryset = queryset.filter(status='DISPONIBLE')

        # Apply django-filter
        filterset = ProductFilter(request.query_params, queryset=queryset)
        queryset = filterset.qs

        # Search (title + description)
        search = request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description_complementaire__icontains=search)
            )

        # EAV dynamic filters
        queryset = _apply_eav_filters(queryset, request.query_params)

        # Ordering with boost priority
        ordering = request.query_params.get('ordering', '-created_at')
        queryset = _apply_boost_ordering(queryset, ordering)

        from rest_framework.pagination import PageNumberPagination  # noqa: local import for APIView
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = ProductListSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = DynamicProductCreateSerializer(
            data=request.data, context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        detail_serializer = ProductDetailSerializer(product, context={'request': request})
        return Response({'data': detail_serializer.data}, status=status.HTTP_201_CREATED)


class ProductDetailAPIView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsProductOwner()]

    def get_object(self, pk):
        from django.shortcuts import get_object_or_404
        return get_object_or_404(
            Product.objects.select_related(
                'ville', 'category', 'seller',
            ).prefetch_related(
                'images', 'attribute_values__attribute',
                'attribute_values__value_choice',
                'attribute_values__value_multi_choice',
            ),
            pk=pk,
        )

    def check_object_permissions(self, request, obj):
        for permission in self.get_permissions():
            if not permission.has_object_permission(request, self, obj):
                self.permission_denied(request)

    def get(self, request, pk):
        product = self.get_object(pk)
        # Deduplicated view tracking
        _track_product_view(request, product)
        serializer = ProductDetailSerializer(product, context={'request': request})
        return Response({'data': serializer.data})

    def patch(self, request, pk):
        product = self.get_object(pk)
        self.check_object_permissions(request, product)
        serializer = DynamicProductCreateSerializer(
            product, data=request.data, partial=True, context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        detail_serializer = ProductDetailSerializer(product, context={'request': request})
        return Response({'data': detail_serializer.data})

    def delete(self, request, pk):
        product = self.get_object(pk)
        self.check_object_permissions(request, product)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ──────────────────────── Helpers ────────────────────────


def _get_client_ip(request):
    """Extract client IP from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _track_product_view(request, product):
    """Track a product view with session-based deduplication."""
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    ip_address = _get_client_ip(request)

    created = False
    if not ProductViewModel.objects.filter(product=product, session_key=session_key).exists():
        ProductViewModel.objects.create(
            product=product,
            session_key=session_key,
            ip_address=ip_address,
        )
        Product.objects.filter(pk=product.pk).update(views_count=F('views_count') + 1)


# ──────────────────────── Favorites API ────────────────────────


class FavoriteListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = Favorite.objects.filter(
            user=request.user,
        ).select_related(
            'product', 'product__ville',
        ).prefetch_related('product__images').order_by('-created_at')

        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = FavoriteSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = FavoriteCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        favorite = serializer.save()
        detail_serializer = FavoriteSerializer(favorite, context={'request': request})
        return Response({'data': detail_serializer.data}, status=status.HTTP_201_CREATED)


class FavoriteDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        from django.shortcuts import get_object_or_404
        favorite = get_object_or_404(Favorite, pk=pk, user=request.user)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ──────────────────────── Report API ────────────────────────


class ProductReportAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        from django.shortcuts import get_object_or_404
        product = get_object_or_404(Product, pk=pk)
        serializer = ReportCreateSerializer(
            data=request.data,
            context={'request': request, 'product': product},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'data': {'message': 'Votre signalement a été envoyé.'}},
            status=status.HTTP_201_CREATED,
        )


# ──────────────────────── WhatsApp Tracking API ────────────────────────


class ProductTrackWhatsAppAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, pk):
        from django.shortcuts import get_object_or_404
        product = get_object_or_404(Product, pk=pk)
        user = request.user if request.user.is_authenticated else None
        ProductWhatsAppClick.objects.create(product=product, user=user)
        Product.objects.filter(pk=pk).update(whatsapp_clicks_count=F('whatsapp_clicks_count') + 1)
        return Response({'data': {'tracked': True}}, status=status.HTTP_201_CREATED)


# ──────────────────────── SSR Views ────────────────────────


class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        queryset = Product.objects.select_related(
            'ville', 'category', 'category__parent', 'seller',
        ).prefetch_related('images').filter(status='DISPONIBLE')

        # URL-based city filter (SEO route)
        city_slug = self.kwargs.get('city_slug', '')
        if city_slug:
            queryset = queryset.filter(ville__slug=city_slug)

        # URL-based category filter (SEO route)
        category_slug = self.kwargs.get('category_slug', '')
        if category_slug:
            queryset = queryset.filter(
                Q(category__slug=category_slug) | Q(category__parent__slug=category_slug)
            )

        # Query param category filters (fallback for form-based filtering)
        if not category_slug:
            cat_param = self.request.GET.get('category', '').strip()
            if cat_param:
                queryset = queryset.filter(category__slug=cat_param)

            cat_root_param = self.request.GET.get('category_root', '').strip()
            if cat_root_param:
                queryset = queryset.filter(category__parent__slug=cat_root_param)

        # Query param city filter (fallback)
        if not city_slug:
            ville = self.request.GET.get('ville', '').strip()
            if ville:
                try:
                    queryset = queryset.filter(ville_id=int(ville))
                except (ValueError, TypeError):
                    pass

        # Price filters
        price_min = self.request.GET.get('price_min', '').strip()
        if price_min:
            try:
                val = float(price_min)
                if val >= 0:
                    queryset = queryset.filter(price__gte=val)
            except (ValueError, TypeError):
                pass

        price_max = self.request.GET.get('price_max', '').strip()
        if price_max:
            try:
                val = float(price_max)
                if val >= 0:
                    queryset = queryset.filter(price__lte=val)
            except (ValueError, TypeError):
                pass

        # Search
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description_complementaire__icontains=search)
            )

        # Seller type
        seller_type = self.request.GET.get('seller_type', '').strip()
        if seller_type:
            queryset = queryset.filter(seller__user_type=seller_type)

        # EAV dynamic filters
        queryset = _apply_eav_filters(queryset, self.request.GET)

        # Ordering with boost priority
        ordering = self.request.GET.get('ordering', '-created_at')
        queryset = _apply_boost_ordering(queryset, ordering)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories_root'] = Category.objects.filter(
            parent__isnull=True,
        ).prefetch_related('children').order_by('order', 'name')
        context['subcategories'] = Category.objects.filter(
            parent__isnull=False,
        ).select_related('parent').order_by('parent__name', 'name')
        context['cities'] = City.objects.all()

        # ── SEO: Resolve city and category from URL kwargs ──
        city_slug = self.kwargs.get('city_slug', '')
        category_slug = self.kwargs.get('category_slug', '')
        current_city = None
        current_category = None

        if city_slug:
            try:
                current_city = City.objects.get(slug=city_slug)
            except City.DoesNotExist:
                pass

        if category_slug:
            try:
                current_category = Category.objects.get(slug=category_slug)
            except Category.DoesNotExist:
                pass

        # Fallback to query params for category name
        if not current_category:
            cat_param = self.request.GET.get('category', '').strip()
            if cat_param:
                try:
                    current_category = Category.objects.get(slug=cat_param)
                except Category.DoesNotExist:
                    pass
            else:
                cat_root_param = self.request.GET.get('category_root', '').strip()
                if cat_root_param:
                    try:
                        current_category = Category.objects.get(slug=cat_root_param)
                    except Category.DoesNotExist:
                        pass

        # Fallback to query params for city name
        if not current_city:
            ville_param = self.request.GET.get('ville', '').strip()
            if ville_param:
                try:
                    current_city = City.objects.get(id=int(ville_param))
                except (City.DoesNotExist, ValueError, TypeError):
                    pass

        # Build SEO strings
        cat_label = current_category.name if current_category else "Matériel Tech & Informatique"
        geo_label = f"à {current_city.name}" if current_city else "au Maroc"

        context['seo_title'] = f"{cat_label} d'occasion {geo_label} | Setup.ma"
        context['seo_h1'] = f"{cat_label} d'occasion {geo_label}"
        context['seo_description'] = (
            f"Achetez et vendez du {cat_label} d'occasion de confiance {geo_label} "
            f"sur Setup.ma. Particuliers et boutiques vérifiées."
        )
        context['current_city'] = current_city
        context['current_category'] = current_category

        # ── Active filters for form re-population ──
        active_filters = {}
        for key in ('category', 'category_root', 'ville', 'price_min', 'price_max',
                     'search', 'seller_type', 'ordering'):
            val = self.request.GET.get(key, '').strip()
            if val:
                active_filters[key] = val
        # Pre-populate from URL kwargs
        if city_slug and 'ville' not in active_filters and current_city:
            active_filters['_city_slug'] = city_slug
        if category_slug and 'category' not in active_filters:
            active_filters['category'] = category_slug

        # EAV filter params
        eav_filter_values = {}
        for key, val in self.request.GET.items():
            if key.startswith('attr_') and val:
                active_filters[key] = val
                try:
                    attr_id = int(key[5:])
                    eav_filter_values[attr_id] = val
                except (ValueError, TypeError):
                    pass

        context['active_filters'] = active_filters
        context['eav_filter_values'] = eav_filter_values

        # Build query string without page for pagination links
        params = self.request.GET.copy()
        params.pop('page', None)
        context['filter_query_string'] = params.urlencode()

        # Filterable attributes for selected subcategory
        effective_cat_slug = category_slug or self.request.GET.get('category', '').strip()
        if effective_cat_slug:
            try:
                cat = Category.objects.get(slug=effective_cat_slug)
                context['filterable_attributes'] = [
                    attr for attr in cat.get_inherited_attributes() if attr.filterable
                ]
            except Category.DoesNotExist:
                context['filterable_attributes'] = []
        else:
            context['filterable_attributes'] = []

        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return Product.objects.select_related(
            'ville', 'category', 'category__parent', 'seller',
        ).prefetch_related(
            'images', 'attribute_values__attribute',
            'attribute_values__value_choice',
            'attribute_values__value_multi_choice',
        )

    def dispatch(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        url_slug = kwargs.get('slug', '')
        if pk:
            try:
                product = Product.objects.only('id', 'title').get(pk=pk)
            except Product.DoesNotExist:
                pass
            else:
                expected_slug = slugify(product.title) or 'produit'
                if url_slug != expected_slug:
                    from django.http import HttpResponsePermanentRedirect
                    return HttpResponsePermanentRedirect(product.get_absolute_url())
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        _track_product_view(self.request, obj)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        phone = product.seller.phone_whatsapp
        if phone:
            clean_phone = phone.lstrip('+').replace(' ', '')
            context['whatsapp_url'] = f"https://wa.me/{clean_phone}"
        # Check if user has favorited this product
        if self.request.user.is_authenticated:
            context['is_favorited'] = Favorite.objects.filter(
                user=self.request.user, product=product,
            ).exists()
            context['has_reported'] = product.reports.filter(
                reporter=self.request.user,
            ).exists()
        # Seller review summary
        from reviews.views import _get_seller_context
        seller_ctx = _get_seller_context(product.seller)
        context['seller_average_rating'] = seller_ctx['average_rating']
        context['seller_reviews_count'] = seller_ctx['reviews_count']
        context['seller_top_tags'] = seller_ctx['top_tags']

        # SEO context
        cat_name = product.category.name
        city_name = product.ville.name
        context['seo_title'] = f"{product.title} — {cat_name} d'occasion à {city_name} | Setup.ma"
        context['seo_description'] = (
            f"{product.title} — {cat_name} d'occasion à {city_name}. "
            f"Prix : {product.price} DH. Contactez le vendeur via WhatsApp sur Setup.ma."
        )
        return context


class ProductCreateView(LoginRequiredMixin, View):

    def get(self, request):
        categories = Category.objects.filter(
            parent__isnull=False,
        ).select_related('parent').order_by('parent__name', 'name')
        cities = City.objects.all()
        return render(request, 'products/product_create.html', {
            'categories': categories,
            'cities': cities,
        })

    def post(self, request):
        categories = Category.objects.filter(
            parent__isnull=False,
        ).select_related('parent').order_by('parent__name', 'name')
        cities = City.objects.all()

        # Build attributes dict from form fields named attr_<id>
        attributes = {}
        for key, value in request.POST.items():
            if key.startswith('attr_') and value:
                attr_id = key.replace('attr_', '')
                attributes[attr_id] = value

        data = {
            'title': request.POST.get('title', ''),
            'description_complementaire': request.POST.get('description_complementaire', ''),
            'price': request.POST.get('price', ''),
            'category': request.POST.get('category', ''),
            'ville': request.POST.get('ville', ''),
            'adresse': request.POST.get('adresse', ''),
            'attributes': attributes,
        }

        images = request.FILES.getlist('images')
        if images:
            data['images'] = images

        serializer = DynamicProductCreateSerializer(
            data=data, context={'request': request},
        )
        if serializer.is_valid():
            product = serializer.save()
            return redirect(product.get_absolute_url())

        return render(request, 'products/product_create.html', {
            'categories': categories,
            'cities': cities,
            'errors': serializer.errors,
            'form_data': request.POST,
        })
