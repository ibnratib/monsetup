from rest_framework import serializers

from catalog.models import AttributeChoice, AttributeDefinition, Category
from core.models import City


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']


class AttributeChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeChoice
        fields = ['id', 'value']


class AttributeDefinitionSerializer(serializers.ModelSerializer):
    choices = AttributeChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = AttributeDefinition
        fields = [
            'id', 'name', 'label_fr', 'attribute_type',
            'required', 'filterable', 'min_value', 'max_value',
            'unit', 'choices', 'depends_on_choice',
        ]


class FilterableAttributeSerializer(serializers.ModelSerializer):
    choices = AttributeChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = AttributeDefinition
        fields = [
            'id', 'name', 'label_fr', 'attribute_type',
            'min_value', 'max_value', 'unit', 'choices', 'depends_on_choice',
        ]


class CategoryListSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'children']

    def get_children(self, obj):
        children = obj.children.all()
        return CategoryListSerializer(children, many=True).data


class CategoryDetailSerializer(serializers.ModelSerializer):
    parent = serializers.SlugRelatedField(slug_field='slug', read_only=True)
    attributes = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'parent', 'attributes']

    def get_attributes(self, obj):
        return AttributeDefinitionSerializer(
            obj.get_inherited_attributes(), many=True
        ).data
