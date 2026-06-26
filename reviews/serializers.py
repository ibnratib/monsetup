from django.conf import settings
from django.db.models import Avg, Count
from rest_framework import serializers

from reviews.models import Review, ReviewReply, ReviewReport, ReviewTag


class ReviewTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewTag
        fields = ['id', 'label']


class ReviewReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewReply
        fields = ['id', 'text', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    reply = ReviewReplySerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'reviewer', 'rating', 'comment', 'tags', 'reply', 'created_at']

    def get_reviewer(self, obj):
        return {
            'id': obj.reviewer_id,
            'first_name': obj.reviewer.first_name,
            'user_type': obj.reviewer.user_type,
        }

    def get_tags(self, obj):
        return list(obj.tags.values_list('label', flat=True))


class ReviewCreateSerializer(serializers.Serializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(
        max_length=settings.MAX_REVIEW_LENGTH,
        required=False,
        allow_blank=True,
        default='',
    )
    tags = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=list,
    )

    def validate_tags(self, value):
        if value:
            existing = set(ReviewTag.objects.filter(id__in=value).values_list('id', flat=True))
            invalid = set(value) - existing
            if invalid:
                raise serializers.ValidationError("Tags invalides.")
        return value

    def validate(self, data):
        request = self.context['request']
        seller = self.context['seller']
        if request.user == seller:
            raise serializers.ValidationError(
                {"non_field_errors": ["Vous ne pouvez pas laisser un avis sur vous-même."]}
            )
        return data

    def create(self, validated_data):
        request = self.context['request']
        seller = self.context['seller']
        tags = validated_data.pop('tags', [])

        review, created = Review.objects.update_or_create(
            reviewer=request.user,
            seller=seller,
            defaults={
                'rating': validated_data['rating'],
                'comment': validated_data.get('comment', ''),
            },
        )
        if tags:
            review.tags.set(tags)
        else:
            review.tags.clear()
        return review


class ReviewReplyCreateSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=settings.MAX_REPLY_LENGTH)

    def validate(self, data):
        request = self.context['request']
        review = self.context['review']
        if request.user != review.seller:
            raise serializers.ValidationError(
                {"non_field_errors": ["Seul le vendeur concerné peut répondre à cet avis."]}
            )
        if hasattr(review, 'reply'):
            raise serializers.ValidationError(
                {"non_field_errors": ["Vous avez déjà répondu à cet avis."]}
            )
        return data

    def create(self, validated_data):
        review = self.context['review']
        return ReviewReply.objects.create(
            review=review,
            text=validated_data['text'],
        )


class ReviewReportSerializer(serializers.Serializer):
    reason = serializers.ChoiceField(choices=ReviewReport.REASON_CHOICES)
    comment = serializers.CharField(max_length=500, required=False, allow_blank=True, default='')

    def validate(self, data):
        request = self.context['request']
        review = self.context['review']
        if ReviewReport.objects.filter(reporter=request.user, review=review).exists():
            raise serializers.ValidationError(
                {"non_field_errors": ["Vous avez déjà signalé cet avis."]}
            )
        return data

    def create(self, validated_data):
        request = self.context['request']
        review = self.context['review']
        return ReviewReport.objects.create(
            reporter=request.user,
            review=review,
            reason=validated_data['reason'],
            comment=validated_data.get('comment', ''),
        )


class SellerReviewSummarySerializer(serializers.Serializer):
    average_rating = serializers.FloatField()
    reviews_count = serializers.IntegerField()
    top_tags = serializers.ListField(child=serializers.CharField())
