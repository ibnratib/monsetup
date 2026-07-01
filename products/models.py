from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from catalog.models import AttributeChoice, AttributeDefinition, Category
from core.models import City, TimeStampedModel


class Product(TimeStampedModel):
    STATUS_CHOICES = [
        ('DISPONIBLE', 'Disponible'),
        ('VENDU', 'Vendu'),
        ('ARCHIVE', 'Archivé'),
    ]

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Vendeur",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name="Catégorie",
    )
    title = models.CharField(max_length=150, verbose_name="Titre")
    description_complementaire = models.TextField(
        blank=True,
        default='',
        max_length=settings.MAX_DESCRIPTION_LENGTH,
        verbose_name="Description complémentaire",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Prix (DH)",
    )
    ville = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name="Ville",
    )
    adresse = models.TextField(blank=True, default='', verbose_name="Adresse")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DISPONIBLE',
        verbose_name="Statut",
    )
    is_boosted = models.BooleanField(default=False, verbose_name="Boosté")
    boost_expires_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Expiration du boost",
    )
    views_count = models.PositiveIntegerField(default=0, verbose_name="Vues")
    whatsapp_clicks_count = models.PositiveIntegerField(
        default=0, verbose_name="Clics WhatsApp",
    )

    class Meta:
        verbose_name = "Annonce"
        verbose_name_plural = "Annonces"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        slug = slugify(self.title) or 'produit'
        return reverse('product-detail', kwargs={'pk': self.pk, 'slug': slug})

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.category_id and self.category.parent is None:
            raise ValidationError({
                'category': "Vous devez choisir une sous-catégorie, pas une catégorie racine."
            })


class ProductImage(TimeStampedModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Annonce",
    )
    image = models.ImageField(upload_to='products/', verbose_name="Image")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")

    class Meta:
        verbose_name = "Image d'annonce"
        verbose_name_plural = "Images d'annonce"
        ordering = ['order']

    def __str__(self):
        return f"Image {self.order} — {self.product.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from products.utils import compress_image
        compress_image(self.image)


class ProductAttributeValue(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='attribute_values',
        verbose_name="Annonce",
    )
    attribute = models.ForeignKey(
        AttributeDefinition,
        on_delete=models.CASCADE,
        related_name='values',
        verbose_name="Attribut",
    )
    value_int = models.IntegerField(null=True, blank=True, verbose_name="Valeur entière")
    value_decimal = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Valeur décimale",
    )
    value_boolean = models.BooleanField(null=True, blank=True, verbose_name="Valeur booléenne")
    value_text = models.CharField(
        max_length=255, blank=True, default='', verbose_name="Valeur texte",
    )
    value_choice = models.ForeignKey(
        AttributeChoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attribute_values',
        verbose_name="Valeur choix",
    )
    value_multi_choice = models.ManyToManyField(
        AttributeChoice,
        blank=True,
        related_name='multi_choice_values',
        verbose_name="Valeurs choix multiples",
    )

    class Meta:
        verbose_name = "Valeur d'attribut"
        verbose_name_plural = "Valeurs d'attributs"
        unique_together = [('product', 'attribute')]

    def __str__(self):
        return f"{self.attribute.name}: {self.get_display_value()}"

    def get_display_value(self):
        attr_type = self.attribute.attribute_type
        if attr_type == 'INT':
            return self.value_int
        elif attr_type == 'DECIMAL':
            return self.value_decimal
        elif attr_type == 'BOOLEAN':
            return self.value_boolean
        elif attr_type == 'TEXT_SHORT':
            return self.value_text
        elif attr_type == 'CHOICE':
            return self.value_choice.value if self.value_choice else None
        elif attr_type == 'MULTI_CHOICE':
            return ', '.join(c.value for c in self.value_multi_choice.all())
        return None


class Favorite(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name="Utilisateur",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name="Annonce",
    )

    class Meta:
        verbose_name = "Favori"
        verbose_name_plural = "Favoris"
        unique_together = [('user', 'product')]

    def __str__(self):
        return f"{self.user.email} — {self.product.title}"


class Report(TimeStampedModel):
    REASON_CHOICES = [
        ('FRAUDULEUSE', 'Annonce frauduleuse'),
        ('PRIX_IRREALISTE', 'Prix irréaliste'),
        ('PRODUIT_INTERDIT', 'Produit interdit'),
        ('CONTENU_INAPPROPRIE', 'Contenu inapproprié'),
        ('DOUBLON', 'Doublon'),
    ]
    STATUS_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('TRAITEE', 'Traitée'),
        ('REJETEE', 'Rejetée'),
    ]

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name="Signaleur",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name="Annonce",
    )
    reason = models.CharField(
        max_length=30,
        choices=REASON_CHOICES,
        verbose_name="Raison",
    )
    comment = models.TextField(
        blank=True,
        default='',
        max_length=500,
        verbose_name="Commentaire",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='EN_ATTENTE',
        verbose_name="Statut",
    )

    class Meta:
        verbose_name = "Signalement"
        verbose_name_plural = "Signalements"
        unique_together = [('reporter', 'product')]

    def __str__(self):
        return f"Signalement: {self.product.title} par {self.reporter.email}"


class ProductView(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_views',
        verbose_name="Annonce",
    )
    session_key = models.CharField(max_length=40, verbose_name="Clé de session")
    ip_address = models.GenericIPAddressField(verbose_name="Adresse IP")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Vue de produit"
        verbose_name_plural = "Vues de produits"
        unique_together = [('product', 'session_key')]

    def __str__(self):
        return f"Vue: {self.product.title} — {self.session_key}"


class ProductWhatsAppClick(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='whatsapp_clicks',
        verbose_name="Annonce",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='whatsapp_clicks',
        verbose_name="Utilisateur",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Clic WhatsApp"
        verbose_name_plural = "Clics WhatsApp"

    def __str__(self):
        return f"Clic WA: {self.product.title}"
