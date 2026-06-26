from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.text import slugify

from accounts.managers import CustomUserManager
from core.models import City, TimeStampedModel


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    USER_TYPE_CHOICES = [
        ('particulier', 'Particulier'),
        ('boutique', 'Boutique'),
    ]

    email = models.EmailField(unique=True, verbose_name="Adresse email")
    phone_whatsapp = models.CharField(max_length=20, blank=True, verbose_name="WhatsApp")
    first_name = models.CharField(max_length=150, blank=True, verbose_name="Prénom")
    last_name = models.CharField(max_length=150, blank=True, verbose_name="Nom")
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, verbose_name="Type")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return self.email

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.email

    def get_short_name(self):
        return self.first_name or self.email


class Particulier(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='particulier',
    )
    max_active_ads = models.PositiveIntegerField(
        default=settings.MAX_ACTIVE_ADS_PARTICULIER,
        verbose_name="Annonces actives max",
    )

    class Meta:
        verbose_name = "Particulier"
        verbose_name_plural = "Particuliers"

    def __str__(self):
        return f"Particulier: {self.user.email}"


class Boutique(TimeStampedModel):
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('VERIFIE', 'Vérifié'),
        ('REJETE', 'Rejeté'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='boutique',
    )
    nom_boutique = models.CharField(max_length=255, verbose_name="Nom de la boutique")
    slug = models.SlugField(unique=True, max_length=255)
    description = models.TextField(blank=True, verbose_name="Description")
    adresse = models.TextField(blank=True, verbose_name="Adresse")
    statut_verification = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='EN_ATTENTE',
        verbose_name="Statut de vérification",
    )
    logo = models.ImageField(upload_to='boutiques/logos/', blank=True, null=True)
    ville = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        related_name='boutiques',
        verbose_name="Ville",
    )

    class Meta:
        verbose_name = "Boutique"
        verbose_name_plural = "Boutiques"

    def __str__(self):
        return self.nom_boutique

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nom_boutique)
            slug = base_slug
            counter = 1
            while Boutique.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
