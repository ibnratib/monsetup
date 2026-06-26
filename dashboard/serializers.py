from rest_framework import serializers

from dashboard.models import Notification
from products.models import Product


class MyProductListSerializer(serializers.ModelSerializer):
    ville = serializers.CharField(source='ville.name', read_only=True)
    category = serializers.CharField(source='category.name', read_only=True)
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'price', 'status', 'ville', 'category',
            'thumbnail', 'views_count', 'whatsapp_clicks_count', 'created_at',
        ]

    def get_thumbnail(self, obj):
        first_image = obj.images.first()
        if first_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(first_image.image.url)
            return first_image.image.url
        return None


class ProductStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[('DISPONIBLE', 'Disponible'), ('VENDU', 'Vendu'), ('ARCHIVE', 'Archivé')],
    )


class DashboardStatsSerializer(serializers.Serializer):
    total_products = serializers.IntegerField()
    total_views = serializers.IntegerField()
    total_whatsapp_clicks = serializers.IntegerField()
    products_disponible = serializers.IntegerField()
    products_vendu = serializers.IntegerField()
    products_archive = serializers.IntegerField()


class NotificationProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title']


class NotificationSerializer(serializers.ModelSerializer):
    product = NotificationProductSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'type', 'message', 'product', 'is_read', 'created_at']
