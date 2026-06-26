from decimal import Decimal, InvalidOperation

from django.conf import settings
from rest_framework import serializers

from catalog.models import AttributeChoice, AttributeDefinition, Category
from core.models import City
from products.models import Favorite, Product, ProductAttributeValue, ProductImage, Report


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'order']


class ProductListSerializer(serializers.ModelSerializer):
    ville = serializers.CharField(source='ville.name', read_only=True)
    category = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    seller_type = serializers.CharField(source='seller.user_type', read_only=True)
    seller_name = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'price', 'status', 'ville', 'category',
            'thumbnail', 'seller_type', 'seller_name', 'is_boosted',
            'created_at',
        ]

    def get_category(self, obj):
        return {'name': obj.category.name, 'slug': obj.category.slug}

    def get_thumbnail(self, obj):
        first_image = obj.images.first()
        if first_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(first_image.image.url)
            return first_image.image.url
        return None

    def get_seller_name(self, obj):
        if obj.seller.user_type == 'boutique' and hasattr(obj.seller, 'boutique'):
            return obj.seller.boutique.nom_boutique
        return obj.seller.get_full_name() or obj.seller.email


class AttributeValueReadSerializer(serializers.ModelSerializer):
    label_fr = serializers.CharField(source='attribute.label_fr', read_only=True)
    attribute_type = serializers.CharField(source='attribute.attribute_type', read_only=True)
    unit = serializers.CharField(source='attribute.unit', read_only=True)
    display_value = serializers.SerializerMethodField()

    class Meta:
        model = ProductAttributeValue
        fields = ['id', 'label_fr', 'attribute_type', 'unit', 'display_value']

    def get_display_value(self, obj):
        return obj.get_display_value()


class SellerPublicSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='pk')
    user_type = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone_whatsapp = serializers.CharField()
    boutique_name = serializers.SerializerMethodField()

    def get_boutique_name(self, obj):
        if obj.user_type == 'boutique' and hasattr(obj, 'boutique'):
            return obj.boutique.nom_boutique
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    attribute_values = AttributeValueReadSerializer(many=True, read_only=True)
    seller = SellerPublicSerializer(read_only=True)
    ville = serializers.CharField(source='ville.name', read_only=True)
    category = serializers.SerializerMethodField()
    whatsapp_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'description_complementaire', 'price', 'status',
            'ville', 'adresse', 'category', 'images', 'attribute_values',
            'seller', 'whatsapp_url', 'is_boosted', 'boost_expires_at',
            'views_count', 'whatsapp_clicks_count', 'created_at', 'updated_at',
        ]

    def get_category(self, obj):
        return {'name': obj.category.name, 'slug': obj.category.slug}

    def get_whatsapp_url(self, obj):
        phone = obj.seller.phone_whatsapp
        if phone:
            clean_phone = phone.lstrip('+').replace(' ', '')
            return f"https://wa.me/{clean_phone}"
        return None


class DynamicProductCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=150)
    description_complementaire = serializers.CharField(
        max_length=settings.MAX_DESCRIPTION_LENGTH, required=False, default='',
    )
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    ville = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())
    adresse = serializers.CharField(required=False, default='')
    status = serializers.ChoiceField(
        choices=Product.STATUS_CHOICES, required=False,
    )
    images = serializers.ListField(
        child=serializers.ImageField(), required=False, default=[],
    )
    attributes = serializers.DictField(required=False, default={})

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le prix doit être supérieur à 0.")
        return value

    def validate_category(self, value):
        if value.parent is None:
            raise serializers.ValidationError(
                "Vous devez choisir une sous-catégorie, pas une catégorie racine."
            )
        return value

    def validate_images(self, value):
        max_images = settings.MAX_IMAGES_PER_PRODUCT
        if len(value) > max_images:
            raise serializers.ValidationError(
                f"Vous ne pouvez pas ajouter plus de {max_images} images."
            )
        return value

    def validate(self, data):
        user = self.context['request'].user

        # Check active ads limit for Particulier
        if user.user_type == 'particulier' and hasattr(user, 'particulier'):
            max_ads = user.particulier.max_active_ads
            active_count = Product.objects.filter(
                seller=user, status='DISPONIBLE',
            ).count()
            if not self.instance and active_count >= max_ads:
                raise serializers.ValidationError({
                    'non_field_errors': [
                        f"Vous avez atteint la limite de {max_ads} annonces actives."
                    ]
                })

        # Validate EAV attributes
        category = data.get('category') or (self.instance.category if self.instance else None)
        if category is None:
            return data

        inherited_attrs = category.get_inherited_attributes()
        valid_attr_ids = {str(a.pk) for a in inherited_attrs}
        attrs_by_id = {str(a.pk): a for a in inherited_attrs}
        submitted = data.get('attributes', {})

        # Reject unknown attributes
        for attr_id in submitted:
            if str(attr_id) not in valid_attr_ids:
                raise serializers.ValidationError({
                    'attributes': [
                        f"L'attribut {attr_id} n'appartient pas à cette catégorie."
                    ]
                })

        # Build set of active choice IDs from submitted values
        # (used to check conditional attribute visibility)
        active_choice_ids = set()
        for attr_id_str, raw_value in submitted.items():
            attr = attrs_by_id.get(str(attr_id_str))
            if attr and attr.attribute_type == 'CHOICE':
                try:
                    active_choice_ids.add(int(raw_value))
                except (ValueError, TypeError):
                    pass

        # Check required attributes (respecting depends_on_choice)
        for attr in inherited_attrs:
            # Skip conditional attributes whose parent choice is not selected
            if attr.depends_on_choice_id is not None:
                if attr.depends_on_choice_id not in active_choice_ids:
                    continue
            if attr.required and str(attr.pk) not in submitted:
                raise serializers.ValidationError({
                    'attributes': [
                        f"L'attribut « {attr.label_fr} » est obligatoire."
                    ]
                })

        # Remove submitted values for inactive conditional attributes
        for attr_id_str in list(submitted.keys()):
            attr = attrs_by_id.get(str(attr_id_str))
            if attr and attr.depends_on_choice_id is not None:
                if attr.depends_on_choice_id not in active_choice_ids:
                    del submitted[attr_id_str]

        # Validate each value
        validated_attrs = {}
        for attr_id_str, raw_value in submitted.items():
            attr = attrs_by_id[str(attr_id_str)]
            validated_attrs[attr.pk] = self._validate_attribute_value(attr, raw_value)

        data['validated_attributes'] = validated_attrs
        return data

    def _validate_attribute_value(self, attr, value):
        attr_type = attr.attribute_type

        if attr_type == 'INT':
            try:
                int_val = int(value)
            except (ValueError, TypeError):
                raise serializers.ValidationError({
                    'attributes': [
                        f"« {attr.label_fr} » doit être un entier."
                    ]
                })
            if attr.min_value is not None and int_val < attr.min_value:
                raise serializers.ValidationError({
                    'attributes': [
                        f"« {attr.label_fr} » doit être ≥ {attr.min_value}."
                    ]
                })
            if attr.max_value is not None and int_val > attr.max_value:
                raise serializers.ValidationError({
                    'attributes': [
                        f"« {attr.label_fr} » doit être ≤ {attr.max_value}."
                    ]
                })
            return {'type': 'INT', 'value': int_val}

        elif attr_type == 'DECIMAL':
            try:
                dec_val = Decimal(str(value))
            except (InvalidOperation, TypeError):
                raise serializers.ValidationError({
                    'attributes': [
                        f"« {attr.label_fr} » doit être un nombre décimal."
                    ]
                })
            if attr.min_value is not None and dec_val < attr.min_value:
                raise serializers.ValidationError({
                    'attributes': [
                        f"« {attr.label_fr} » doit être ≥ {attr.min_value}."
                    ]
                })
            if attr.max_value is not None and dec_val > attr.max_value:
                raise serializers.ValidationError({
                    'attributes': [
                        f"« {attr.label_fr} » doit être ≤ {attr.max_value}."
                    ]
                })
            return {'type': 'DECIMAL', 'value': dec_val}

        elif attr_type == 'BOOLEAN':
            if not isinstance(value, bool):
                raise serializers.ValidationError({
                    'attributes': [
                        f"« {attr.label_fr} » doit être un booléen."
                    ]
                })
            return {'type': 'BOOLEAN', 'value': value}

        elif attr_type == 'TEXT_SHORT':
            str_val = str(value)
            if len(str_val) > 255:
                raise serializers.ValidationError({
                    'attributes': [
                        f"« {attr.label_fr} » ne doit pas dépasser 255 caractères."
                    ]
                })
            return {'type': 'TEXT_SHORT', 'value': str_val}

        elif attr_type == 'CHOICE':
            try:
                choice = AttributeChoice.objects.get(pk=int(value), attribute=attr)
            except (AttributeChoice.DoesNotExist, ValueError, TypeError):
                raise serializers.ValidationError({
                    'attributes': [
                        f"Choix invalide pour « {attr.label_fr} »."
                    ]
                })
            return {'type': 'CHOICE', 'value': choice}

        elif attr_type == 'MULTI_CHOICE':
            if not isinstance(value, list):
                raise serializers.ValidationError({
                    'attributes': [
                        f"« {attr.label_fr} » attend une liste de choix."
                    ]
                })
            try:
                ids = [int(v) for v in value]
            except (ValueError, TypeError):
                raise serializers.ValidationError({
                    'attributes': [
                        f"Choix invalides pour « {attr.label_fr} »."
                    ]
                })
            choices = AttributeChoice.objects.filter(pk__in=ids, attribute=attr)
            if choices.count() != len(ids):
                raise serializers.ValidationError({
                    'attributes': [
                        f"Certains choix sont invalides pour « {attr.label_fr} »."
                    ]
                })
            return {'type': 'MULTI_CHOICE', 'value': list(choices)}

        raise serializers.ValidationError({
            'attributes': [f"Type d'attribut inconnu pour « {attr.label_fr} »."]
        })

    def create(self, validated_data):
        images = validated_data.pop('images', [])
        validated_attrs = validated_data.pop('validated_attributes', {})
        validated_data.pop('attributes', None)

        product = Product.objects.create(
            seller=self.context['request'].user,
            **validated_data,
        )

        # Create images
        for i, image_file in enumerate(images):
            ProductImage.objects.create(product=product, image=image_file, order=i)

        # Create attribute values
        self._save_attribute_values(product, validated_attrs)

        return product

    def update(self, instance, validated_data):
        images = validated_data.pop('images', None)
        validated_attrs = validated_data.pop('validated_attributes', {})
        validated_data.pop('attributes', None)

        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()

        # Replace images if new ones provided
        if images is not None and len(images) > 0:
            instance.images.all().delete()
            for i, image_file in enumerate(images):
                ProductImage.objects.create(product=instance, image=image_file, order=i)

        # Replace attribute values
        if validated_attrs:
            instance.attribute_values.all().delete()
            self._save_attribute_values(instance, validated_attrs)

        return instance

    def _save_attribute_values(self, product, validated_attrs):
        for attr_id, attr_data in validated_attrs.items():
            attr_def = AttributeDefinition.objects.get(pk=attr_id)
            pav = ProductAttributeValue(product=product, attribute=attr_def)

            if attr_data['type'] == 'INT':
                pav.value_int = attr_data['value']
            elif attr_data['type'] == 'DECIMAL':
                pav.value_decimal = attr_data['value']
            elif attr_data['type'] == 'BOOLEAN':
                pav.value_boolean = attr_data['value']
            elif attr_data['type'] == 'TEXT_SHORT':
                pav.value_text = attr_data['value']
            elif attr_data['type'] == 'CHOICE':
                pav.value_choice = attr_data['value']
            elif attr_data['type'] == 'MULTI_CHOICE':
                pav.save()
                pav.value_multi_choice.set(attr_data['value'])
                continue

            pav.save()


class FavoriteProductSerializer(serializers.ModelSerializer):
    """Nested product info for favorite listing."""
    ville = serializers.CharField(source='ville.name', read_only=True)
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'price', 'status', 'ville', 'thumbnail']

    def get_thumbnail(self, obj):
        first_image = obj.images.first()
        if first_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(first_image.image.url)
            return first_image.image.url
        return None


class FavoriteSerializer(serializers.ModelSerializer):
    product = FavoriteProductSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'product', 'created_at']


class FavoriteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['product']

    def validate_product(self, value):
        user = self.context['request'].user
        if Favorite.objects.filter(user=user, product=value).exists():
            raise serializers.ValidationError("Ce produit est déjà dans vos favoris.")
        return value

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['reason', 'comment']

    def validate(self, data):
        user = self.context['request'].user
        product = self.context['product']

        if product.seller == user:
            raise serializers.ValidationError(
                "Vous ne pouvez pas signaler votre propre annonce."
            )
        if Report.objects.filter(reporter=user, product=product).exists():
            raise serializers.ValidationError(
                "Vous avez déjà signalé cette annonce."
            )
        return data

    def create(self, validated_data):
        validated_data['reporter'] = self.context['request'].user
        validated_data['product'] = self.context['product']
        return super().create(validated_data)
