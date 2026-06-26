from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.models import TimeStampedModel


class ReviewTag(models.Model):
    label = models.CharField(max_length=50, unique=True, verbose_name="Label")

    class Meta:
        verbose_name = "Tag d'avis"
        verbose_name_plural = "Tags d'avis"
        ordering = ['label']

    def __str__(self):
        return self.label


class Review(TimeStampedModel):
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='given_reviews',
        verbose_name="Auteur",
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_reviews',
        verbose_name="Vendeur",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Note",
    )
    comment = models.TextField(
        max_length=settings.MAX_REVIEW_LENGTH,
        blank=True,
        default='',
        verbose_name="Commentaire",
    )
    tags = models.ManyToManyField(
        ReviewTag,
        blank=True,
        related_name='reviews',
        verbose_name="Tags",
    )

    class Meta:
        verbose_name = "Avis"
        verbose_name_plural = "Avis"
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['reviewer', 'seller'],
                name='unique_review_per_seller',
            ),
        ]

    def __str__(self):
        return f"Avis de {self.reviewer} sur {self.seller} ({self.rating}/5)"


class ReviewReply(TimeStampedModel):
    review = models.OneToOneField(
        Review,
        on_delete=models.CASCADE,
        related_name='reply',
        verbose_name="Avis",
    )
    text = models.TextField(
        max_length=settings.MAX_REPLY_LENGTH,
        verbose_name="Réponse",
    )

    class Meta:
        verbose_name = "Réponse à un avis"
        verbose_name_plural = "Réponses aux avis"

    def __str__(self):
        return f"Réponse à l'avis #{self.review_id}"


class ReviewReport(TimeStampedModel):
    REASON_CHOICES = [
        ('FAUX_AVIS', 'Faux avis'),
        ('DIFFAMATION', 'Diffamation'),
        ('CONTENU_INAPPROPRIE', 'Contenu inapproprié'),
        ('SPAM', 'Spam'),
    ]
    STATUS_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('TRAITEE', 'Traitée'),
        ('REJETEE', 'Rejetée'),
    ]

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='review_reports',
        verbose_name="Signaleur",
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name="Avis signalé",
    )
    reason = models.CharField(
        max_length=30,
        choices=REASON_CHOICES,
        verbose_name="Raison",
    )
    comment = models.TextField(
        max_length=500,
        blank=True,
        default='',
        verbose_name="Commentaire",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='EN_ATTENTE',
        verbose_name="Statut",
    )

    class Meta:
        verbose_name = "Signalement d'avis"
        verbose_name_plural = "Signalements d'avis"
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['reporter', 'review'],
                name='unique_report_per_review',
            ),
        ]

    def __str__(self):
        return f"Signalement de l'avis #{self.review_id} par {self.reporter}"
