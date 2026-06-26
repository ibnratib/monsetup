from rest_framework import serializers


class ChatMessageSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=500)


class AISearchResponseSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=['question', 'search'])
    message = serializers.CharField()
    products = serializers.ListField(child=serializers.DictField(), required=False)
    filters_applied = serializers.DictField(required=False)
    total_results = serializers.IntegerField(required=False)
