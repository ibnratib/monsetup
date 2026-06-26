from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import Notification
from products.models import Product


class Command(BaseCommand):
    help = "Crée les notifications de rappel pour les annonces disponibles depuis plus de 30 jours sans changement."

    def handle(self, *args, **options):
        reminder_days = getattr(settings, 'AD_REMINDER_DAYS', 30)
        cutoff = timezone.now() - timezone.timedelta(days=reminder_days)

        stale_products = Product.objects.filter(
            status='DISPONIBLE',
            updated_at__lt=cutoff,
        ).select_related('seller')

        created_count = 0
        for product in stale_products:
            # Vérifier qu'il n'existe pas déjà une notification RAPPEL_DISPONIBILITE non lue
            already_exists = Notification.objects.filter(
                product=product,
                type='RAPPEL_DISPONIBILITE',
                is_read=False,
            ).exists()

            if not already_exists:
                Notification.objects.create(
                    user=product.seller,
                    type='RAPPEL_DISPONIBILITE',
                    message=f"Votre annonce « {product.title} » est en ligne depuis plus de {reminder_days} jours. Est-elle toujours disponible ?",
                    product=product,
                )
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"{created_count} notification(s) de rappel créée(s).")
        )
