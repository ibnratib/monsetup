from django.conf import settings
from django.db import models

from core.models import TimeStampedModel
from products.models import Product


class Notification(TimeStampedModel):
    TYPE_CHOICES = [
        ('RAPPEL_DISPONIBILITE', 'Rappel de disponibilité'),
        ('SIGNALEMENT_RECU', 'Signalement reçu'),
        ('ANNONCE_EXPIREE', 'Annonce expirée'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="Utilisateur",
    )
    type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        verbose_name="Type",
    )
    message = models.TextField(verbose_name="Message")
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name="Annonce",
    )
    is_read = models.BooleanField(default=False, verbose_name="Lu")

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_type_display()}] {self.user} — {self.message[:50]}"
