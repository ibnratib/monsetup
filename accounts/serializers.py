import re

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from accounts.models import Boutique, Particulier
from core.models import City

User = get_user_model()

PHONE_REGEX = re.compile(r'^0[67]\d{8}$')


def validate_phone_whatsapp(value):
    if value and not PHONE_REGEX.match(value):
        raise serializers.ValidationError(
            "Format invalide. Utilisez le format marocain : 06XXXXXXXX ou 07XXXXXXXX."
        )
    return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone_whatsapp', 'user_type', 'date_joined']
        read_only_fields = ['id', 'email', 'user_type', 'date_joined']


class ParticulierSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Particulier
        fields = ['user', 'max_active_ads']


class BoutiqueSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Boutique
        fields = ['user', 'nom_boutique', 'slug', 'description', 'adresse', 'ville', 'statut_verification', 'logo']
        read_only_fields = ['slug', 'statut_verification']


class ProfileSerializer(serializers.Serializer):
    """Sérialise le user + son profil dynamiquement."""

    def to_representation(self, instance):
        user_data = UserSerializer(instance).data
        if instance.user_type == 'particulier' and hasattr(instance, 'particulier'):
            user_data['profil'] = {
                'max_active_ads': instance.particulier.max_active_ads,
            }
        elif instance.user_type == 'boutique' and hasattr(instance, 'boutique'):
            user_data['profil'] = BoutiqueSerializer(instance.boutique).data
            del user_data['profil']['user']
        return user_data

    def update(self, instance, validated_data):
        return instance


class RegisterParticulierSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    phone_whatsapp = serializers.CharField(max_length=20, required=False, default='')

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Un compte avec cet email existe déjà.")
        return value.lower()

    def validate_phone_whatsapp(self, value):
        return validate_phone_whatsapp(value)

    @transaction.atomic
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_whatsapp=validated_data.get('phone_whatsapp', ''),
            user_type='particulier',
        )
        Particulier.objects.create(user=user)
        return user


class RegisterBoutiqueSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    nom_boutique = serializers.CharField(max_length=255)
    phone_whatsapp = serializers.CharField(max_length=20, required=False, default='')
    adresse = serializers.CharField(required=False, default='')
    ville = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Un compte avec cet email existe déjà.")
        return value.lower()

    def validate_phone_whatsapp(self, value):
        return validate_phone_whatsapp(value)

    @transaction.atomic
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            phone_whatsapp=validated_data.get('phone_whatsapp', ''),
            user_type='boutique',
        )
        Boutique.objects.create(
            user=user,
            nom_boutique=validated_data['nom_boutique'],
            adresse=validated_data.get('adresse', ''),
            ville=validated_data['ville'],
        )
        return user


class MeUpdateSerializer(serializers.ModelSerializer):
    """Mise à jour du profil utilisateur (champs modifiables uniquement)."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_whatsapp']

    def validate_phone_whatsapp(self, value):
        return validate_phone_whatsapp(value)
